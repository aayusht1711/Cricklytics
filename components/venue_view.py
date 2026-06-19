import streamlit as st
import pandas as pd
import plotly.graph_objects as go


@st.cache_data
def _venue_stats(data):
    # --- Avg 1st innings score per venue ---
    inn1 = (
        data[data["innings"] == 1]
        .groupby(["match_id", "venue"])["runs_total"]
        .sum()
        .reset_index()
    )
    avg_score = (
        inn1.groupby("venue")["runs_total"]
        .agg(avg_first_innings="mean", matches="count")
        .reset_index()
    )

    # --- Chasing win % per venue ---
    match_df = data.drop_duplicates("match_id")[
        ["match_id", "venue", "win_outcome"]
    ].copy()
    match_df["chasing_won"] = match_df["win_outcome"].str.contains(
        "wickets", na=False
    )
    chase = (
        match_df.groupby("venue")
        .agg(total_matches=("match_id", "count"), chasing_wins=("chasing_won", "sum"))
        .reset_index()
    )
    chase["chase_win_pct"] = (
        chase["chasing_wins"] / chase["total_matches"] * 100
    ).round(1)

    # --- Merge ---
    venue_df = avg_score.merge(chase, on="venue")
    venue_df = venue_df[venue_df["total_matches"] >= 5]
    venue_df["avg_first_innings"] = venue_df["avg_first_innings"].round(1)

    # --- Ground rating: >50% chase = Batting Paradise, else Bowling ---
    venue_df["ground_type"] = venue_df["chase_win_pct"].apply(
        lambda x: "🏏 Batting Paradise" if x >= 50 else "🎯 Bowler's Ground"
    )

    return venue_df


@st.cache_data
def _toss_stats(data):
    match_df = data.drop_duplicates("match_id")[
        ["match_id", "venue", "toss_winner", "toss_decision", "match_won_by"]
    ].copy()
    match_df["toss_match_winner"] = (
        match_df["toss_winner"] == match_df["match_won_by"]
    )
    match_df["toss_bat"] = match_df["toss_decision"] == "bat"
    match_df["toss_field"] = match_df["toss_decision"] == "field"
    
    match_df["toss_bat_win"] = match_df["toss_match_winner"] & match_df["toss_bat"]
    match_df["toss_field_win"] = match_df["toss_match_winner"] & match_df["toss_field"]

    toss = (
        match_df.groupby("venue")
        .agg(
            toss_wins_match=("toss_match_winner", "sum"),
            toss_bat_total=("toss_bat", "sum"),
            toss_field_total=("toss_field", "sum"),
            toss_bat_wins=("toss_bat_win", "sum"),
            toss_field_wins=("toss_field_win", "sum"),
            total=("match_id", "count"),
        )
        .reset_index()
    )
    toss["toss_win_pct"] = (toss["toss_wins_match"] / toss["total"] * 100).round(1)
    
    toss["toss_bat_win_pct"] = (toss["toss_bat_wins"] / toss["toss_bat_total"].replace(0, 1) * 100).round(1)
    toss["toss_field_win_pct"] = (toss["toss_field_wins"] / toss["toss_field_total"].replace(0, 1) * 100).round(1)
    
    return toss[toss["total"] >= 5]


def show_venue_view(data):
    st.markdown("<h2>🏟️ Venue Intelligence</h2>", unsafe_allow_html=True)

    venue_df = _venue_stats(data)
    toss_df = _toss_stats(data)

    # Venue selector
    venues = sorted(venue_df["venue"].unique())
    selected_venue = st.selectbox("Select Venue", venues)

    row = venue_df[venue_df["venue"] == selected_venue].iloc[0]
    toss_row = toss_df[toss_df["venue"] == selected_venue]

    toss_pct = toss_row["toss_win_pct"].values[0] if not toss_row.empty else "N/A"

    # --- Main stats card ---
    st.markdown(
        f"""
    <div class='card'>
        <h3 style='color:#00FFFF;'>📍 {selected_venue}</h3>
        <table style='width:100%; color:white; font-size:15px; margin-top:10px;'>
            <tr>
                <td>🏏 Avg 1st Innings Score</td>
                <td><b>{row['avg_first_innings']}</b></td>
                <td>🎯 Chasing Win %</td>
                <td><b>{row['chase_win_pct']}%</b></td>
            </tr>
            <tr>
                <td>📊 Matches Played</td>
                <td><b>{int(row['total_matches'])}</b></td>
                <td>🪙 Toss → Match Win %</td>
                <td><b>{toss_pct}%</b></td>
            </tr>
            <tr>
                <td>☀️ Toss & Bat First Win %</td>
                <td><b style='color:#FFE66D;'>{toss_row["toss_bat_win_pct"].values[0] if not toss_row.empty else "N/A"}%</b></td>
                <td>🌙 Toss & Bowl First Win %</td>
                <td><b style='color:#4ECDC4;'>{toss_row["toss_field_win_pct"].values[0] if not toss_row.empty else "N/A"}%</b></td>
            </tr>
            <tr>
                <td colspan='4' style='padding-top:10px;'>Ground Type: <b>{row['ground_type']}</b></td>
            </tr>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # --- Top batters at this venue ---
    st.markdown("<h3>🔥 Top Run Scorers at This Venue</h3>", unsafe_allow_html=True)
    venue_data = data[data["venue"] == selected_venue]
    top_bat = (
        venue_data.groupby("batter")["runs_batter"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    for i, (player, runs) in enumerate(top_bat.items(), 1):
        st.markdown(
            f"<div class='card'>#{i} &nbsp; 🏏 <b>{player}</b> — {runs} runs</div>",
            unsafe_allow_html=True,
        )

    # --- Top bowlers at this venue ---
    st.markdown("<h3>🎯 Top Wicket Takers at This Venue</h3>", unsafe_allow_html=True)
    top_bowl = (
        venue_data.groupby("bowler")["bowler_wicket"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    for i, (player, wkts) in enumerate(top_bowl.items(), 1):
        st.markdown(
            f"<div class='card'>#{i} &nbsp; ⚡ <b>{player}</b> — {wkts} wickets</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Global leaderboard charts ---
    st.markdown("<h3>📊 All Venues — Avg 1st Innings Score</h3>", unsafe_allow_html=True)
    top_venues = venue_df.sort_values("avg_first_innings", ascending=False).head(12).copy()
    top_venues["short_name"] = top_venues["venue"].apply(lambda v: v.split(",")[0][:28])
    top_venues["color"] = top_venues["venue"].apply(lambda v: "#00FFFF" if v == selected_venue else "#1f77b4")
    
    fig = go.Figure(go.Bar(
        x=top_venues["avg_first_innings"], y=top_venues["short_name"],
        orientation="h", marker_color=top_venues["color"],
        text=top_venues["avg_first_innings"],
        textposition="outside",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="white"),
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(autorange="reversed"),
        xaxis_title="Avg 1st Innings Score"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Chase win % chart ---
    st.markdown("<h3>🏃 Chasing Win % by Venue (min 5 matches)</h3>", unsafe_allow_html=True)
    chase_sorted = venue_df.sort_values("chase_win_pct", ascending=False).head(12).copy()
    chase_sorted["short_name"] = chase_sorted["venue"].apply(lambda v: v.split(",")[0][:28])
    chase_sorted["color"] = chase_sorted["chase_win_pct"].apply(lambda p: "#FF6B6B" if p >= 50 else "#4ECDC4")
    
    fig2 = go.Figure(go.Bar(
        x=chase_sorted["chase_win_pct"], y=chase_sorted["short_name"],
        orientation="h", marker_color=chase_sorted["color"],
        text=chase_sorted["chase_win_pct"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ))
    fig2.add_vline(x=50, line_dash="dash", line_color="rgba(255,255,255,0.5)")
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="white"),
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(autorange="reversed"),
        xaxis_title="Chasing Win %"
    )
    st.plotly_chart(fig2, use_container_width=True)
