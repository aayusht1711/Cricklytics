import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


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
    toss = (
        match_df.groupby("venue")
        .agg(
            toss_wins_match=("toss_match_winner", "sum"),
            total=("match_id", "count"),
        )
        .reset_index()
    )
    toss["toss_win_pct"] = (toss["toss_wins_match"] / toss["total"] * 100).round(1)
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
    top_venues = venue_df.sort_values("avg_first_innings", ascending=False).head(12)

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    colors = [
        "#00FFFF" if v == selected_venue else "#1f77b4"
        for v in top_venues["venue"]
    ]
    short_names = [v.split(",")[0][:28] for v in top_venues["venue"]]

    bars = ax.barh(short_names, top_venues["avg_first_innings"], color=colors)
    ax.set_xlabel("Avg 1st Innings Score", color="white")
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#444")
    for bar in bars:
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.0f}",
            va="center",
            color="white",
            fontsize=8,
        )

    highlight = mpatches.Patch(color="#00FFFF", label="Selected Venue")
    ax.legend(handles=[highlight], facecolor="#0e1117", labelcolor="white")
    plt.tight_layout()
    st.pyplot(fig)

    # --- Chase win % chart ---
    st.markdown("<h3>🏃 Chasing Win % by Venue (min 5 matches)</h3>", unsafe_allow_html=True)
    chase_sorted = venue_df.sort_values("chase_win_pct", ascending=False).head(12)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    fig2.patch.set_facecolor("#0e1117")
    ax2.set_facecolor("#0e1117")

    colors2 = [
        "#FF6B6B" if p >= 50 else "#4ECDC4" for p in chase_sorted["chase_win_pct"]
    ]
    short_names2 = [v.split(",")[0][:28] for v in chase_sorted["venue"]]

    ax2.barh(short_names2, chase_sorted["chase_win_pct"], color=colors2)
    ax2.axvline(50, color="white", linestyle="--", alpha=0.5, label="50% line")
    ax2.set_xlabel("Chasing Win %", color="white")
    ax2.tick_params(colors="white")
    ax2.spines[:].set_color("#444")

    bat_patch = mpatches.Patch(color="#FF6B6B", label="Batting Paradise (>50%)")
    bowl_patch = mpatches.Patch(color="#4ECDC4", label="Bowler's Ground (<50%)")
    ax2.legend(handles=[bat_patch, bowl_patch], facecolor="#0e1117", labelcolor="white")
    plt.tight_layout()
    st.pyplot(fig2)
