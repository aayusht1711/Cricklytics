import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


TEAM_COLORS = {
    "Mumbai Indians": "#005DA0", "Chennai Super Kings": "#F7C010",
    "Royal Challengers Bangalore": "#EC1C24", "Royal Challengers Bengaluru": "#EC1C24",
    "Kolkata Knight Riders": "#3A225D", "Rajasthan Royals": "#EA1A85",
    "Sunrisers Hyderabad": "#F7700E", "Delhi Daredevils": "#0078BC",
    "Delhi Capitals": "#0078BC", "Kings XI Punjab": "#DCDDDF",
    "Punjab Kings": "#ED1B24", "Deccan Chargers": "#FDB933",
    "Gujarat Titans": "#1C4966", "Lucknow Super Giants": "#A72056",
}


@st.cache_data
def _build_player_pool(data):
    """Build batting, bowling and all-rounder pools with ratings."""

    # ── BATTING POOL ─────────────────────────────────────────────
    bat = data.groupby("batter").agg(
        runs    =("runs_batter", "sum"),
        balls   =("balls_faced", "sum"),
        sixes   =("runs_batter", lambda x: (x == 6).sum()),
        fours   =("runs_batter", lambda x: (x == 4).sum()),
        team    =("batting_team", lambda x: x.value_counts().index[0]),
    ).reset_index()
    bat = bat[bat["balls"] >= 200].copy()
    bat["sr"]          = (bat["runs"] / bat["balls"] * 100).round(1)
    bat["boundary_pct"]= ((bat["fours"] + bat["sixes"]) / bat["balls"] * 100).round(1)

    # dismissals
    if "player_dismissed" in data.columns:
        dis = data[data["player_dismissed"].notna()].groupby("player_dismissed").size().reset_index(name="outs")
        bat = bat.merge(dis, left_on="batter", right_on="player_dismissed", how="left").fillna({"outs": 1})
        bat["avg"] = (bat["runs"] / bat["outs"]).round(1)
    else:
        bat["avg"] = bat["runs"] / 30

    # match-level 50s and 100s
    match_runs = data.groupby(["match_id","batter"])["runs_batter"].sum().reset_index()
    match_runs["is_50"]  = ((match_runs["runs_batter"] >= 50) & (match_runs["runs_batter"] < 100)).astype(int)
    match_runs["is_100"] = (match_runs["runs_batter"] >= 100).astype(int)
    milestone = match_runs.groupby("batter").agg(fifties=("is_50","sum"), hundreds=("is_100","sum")).reset_index()
    bat = bat.merge(milestone, on="batter", how="left").fillna(0)

    # Powerplay SR
    pp = data[data["over"] <= 5].groupby("batter").agg(
        pp_runs =("runs_batter","sum"),
        pp_balls=("balls_faced","sum"),
    ).reset_index()
    pp["pp_sr"] = (pp["pp_runs"] / pp["pp_balls"] * 100).round(1)
    bat = bat.merge(pp, on="batter", how="left").fillna({"pp_sr": 0})

    # Batter rating (0-100)
    bat["bat_rating"] = (
        bat["runs"].clip(0, 8000) / 8000 * 35 +
        bat["sr"].clip(0, 200)   / 200  * 25 +
        bat["avg"].clip(0, 60)   / 60   * 20 +
        (bat["fifties"] + bat["hundreds"] * 2).clip(0, 50) / 50 * 20
    ).round(1)

    # ── BOWLING POOL ──────────────────────────────────────────────
    runs_bowl_col = "runs_bowler" if "runs_bowler" in data.columns else "runs_total"
    bowl = data.groupby("bowler").agg(
        wickets =("bowler_wicket",  "sum"),
        runs_c  =(runs_bowl_col,   "sum"),
        balls   =("valid_ball",    "sum"),
        team    =("batting_team",  lambda x: x.value_counts().index[0]),
    ).reset_index()
    bowl = bowl[bowl["balls"] >= 120].copy()
    bowl["economy"]    = (bowl["runs_c"] / bowl["balls"] * 6).round(2)
    bowl["bowling_sr"] = (bowl["balls"]  / bowl["wickets"].replace(0, np.nan)).round(1)

    # Death overs economy
    runs_bowl_col2 = "runs_bowler" if "runs_bowler" in data.columns else "runs_total"
    death = data[data["over"] >= 15].groupby("bowler").agg(
        d_runs =(runs_bowl_col2, "sum"),
        d_balls=("valid_ball",   "sum"),
    ).reset_index()
    death["death_econ"] = (death["d_runs"] / death["d_balls"] * 6).round(2)
    bowl = bowl.merge(death, on="bowler", how="left").fillna({"death_econ": 9.0})

    # Bowler rating (0-100)
    bowl["bowl_rating"] = (
        bowl["wickets"].clip(0, 200) / 200 * 40 +
        (10 - bowl["economy"].clip(5, 10)) / 5 * 35 +
        (40  - bowl["bowling_sr"].clip(10, 40).fillna(40)) / 30 * 25
    ).round(1)

    # ── ALL ROUNDERS ─────────────────────────────────────────────
    both = set(bat["batter"].tolist()) & set(bowl["bowler"].tolist())
    ar_bat  = bat[bat["batter"].isin(both)][["batter","bat_rating","runs","sr","team"]].copy()
    ar_bowl = bowl[bowl["bowler"].isin(both)][["bowler","bowl_rating","wickets","economy"]].copy()
    ar      = ar_bat.merge(ar_bowl, left_on="batter", right_on="bowler")
    ar["ar_rating"] = (ar["bat_rating"] * 0.5 + ar["bowl_rating"] * 0.5).round(1)

    # ── KEEPER POOL ───────────────────────────────────────────────
    keepers = ["MS Dhoni","KD Karthik","RV Uthappa","WP Saha","RR Pant",
                "SV Samson","Q de Kock","AB de Villiers","KL Rahul","Ishan Kishan"]
    keep_df = bat[bat["batter"].isin(keepers)][["batter","bat_rating","runs","sr","team"]].copy()

    return bat, bowl, ar, keep_df


def _radar(players_data, label, color):
    """Spider chart for team profile."""
    categories = ["Batting\nPower", "Strike\nRate", "Bowling\nAttack",
                  "Economy", "All\nRound"]
    values = [
        min(100, players_data.get("avg_bat_rating", 50)),
        min(100, players_data.get("avg_sr", 130) / 2),
        min(100, players_data.get("avg_bowl_rating", 40)),
        min(100, (10 - players_data.get("avg_econ", 8)) / 4 * 100),
        min(100, players_data.get("ar_count", 0) / 4 * 100),
    ]
    values += [values[0]]
    N      = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")
    ax.plot(angles, values, color=color, linewidth=2)
    ax.fill(angles, values, alpha=0.2, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color="white", fontsize=7)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["", "", "", ""], fontsize=0)
    ax.spines["polar"].set_color("#333")
    ax.grid(color="#333", linewidth=0.5)
    ax.set_title(label, color="white", fontsize=10, pad=12)
    plt.tight_layout()
    return fig


def _compute_team_rating(selected_players, bat_df, bowl_df, ar_df):
    """Compute overall team rating out of 100."""
    scores = []

    for p in selected_players:
        b = bat_df[bat_df["batter"] == p]
        if not b.empty:
            scores.append(float(b.iloc[0]["bat_rating"]))

        bw = bowl_df[bowl_df["bowler"] == p]
        if not bw.empty:
            scores.append(float(bw.iloc[0]["bowl_rating"]))

    if not scores:
        return 0, {}

    avg_bat  = float(bat_df[bat_df["batter"].isin(selected_players)]["bat_rating"].mean()) \
               if not bat_df[bat_df["batter"].isin(selected_players)].empty else 50
    avg_sr   = float(bat_df[bat_df["batter"].isin(selected_players)]["sr"].mean()) \
               if not bat_df[bat_df["batter"].isin(selected_players)].empty else 130
    avg_bowl = float(bowl_df[bowl_df["bowler"].isin(selected_players)]["bowl_rating"].mean()) \
               if not bowl_df[bowl_df["bowler"].isin(selected_players)].empty else 40
    avg_econ = float(bowl_df[bowl_df["bowler"].isin(selected_players)]["economy"].mean()) \
               if not bowl_df[bowl_df["bowler"].isin(selected_players)].empty else 8.0
    ar_count = len(ar_df[ar_df["batter"].isin(selected_players)])

    overall = round(
        avg_bat * 0.35 +
        avg_bowl * 0.35 +
        min(100, (10 - avg_econ) / 4 * 100) * 0.15 +
        min(100, ar_count / 4 * 100) * 0.15,
        1,
    )

    return min(100, overall), {
        "avg_bat_rating": avg_bat,
        "avg_sr":         avg_sr,
        "avg_bowl_rating":avg_bowl,
        "avg_econ":       avg_econ,
        "ar_count":       ar_count,
    }


def show_dreamxi_view(data):
    st.markdown("<h2>Build Your Dream XI</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5);margin-bottom:20px;'>"
        "Pick 11 players — max 4 from one team. "
        "Get an instant team rating based on real career stats.</p>",
        unsafe_allow_html=True,
    )

    bat_df, bowl_df, ar_df, keep_df = _build_player_pool(data)

    # ── ROLE-BASED SELECTION ──────────────────────────────────────
    st.markdown("<h3>Step 1 — Pick Your Playing XI</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<p style='color:#FFE66D;font-weight:700;margin-bottom:4px;'>Wicket Keeper (pick 1)</p>",
            unsafe_allow_html=True,
        )
        keeper = st.selectbox(
            "Keeper",
            keep_df.sort_values("bat_rating", ascending=False)["batter"].tolist(),
            label_visibility="collapsed",
        )

        st.markdown(
            "<p style='color:#00FFFF;font-weight:700;margin:12px 0 4px;'>Batters (pick 4)</p>",
            unsafe_allow_html=True,
        )
        pure_bat = bat_df[~bat_df["batter"].isin(
            ar_df["batter"].tolist() + keep_df["batter"].tolist()
        )].sort_values("bat_rating", ascending=False)
        batters = st.multiselect(
            "Batters",
            pure_bat["batter"].tolist(),
            default=pure_bat["batter"].tolist()[:4],
            max_selections=4,
            label_visibility="collapsed",
        )

        st.markdown(
            "<p style='color:#4ECDC4;font-weight:700;margin:12px 0 4px;'>All Rounders (pick 2)</p>",
            unsafe_allow_html=True,
        )
        ar_sorted = ar_df.sort_values("ar_rating", ascending=False)
        allrounders = st.multiselect(
            "All Rounders",
            ar_sorted["batter"].tolist(),
            default=ar_sorted["batter"].tolist()[:2],
            max_selections=2,
            label_visibility="collapsed",
        )

    with col2:
        st.markdown(
            "<p style='color:#FF6B6B;font-weight:700;margin-bottom:4px;'>Bowlers (pick 4)</p>",
            unsafe_allow_html=True,
        )
        pure_bowl = bowl_df[~bowl_df["bowler"].isin(
            ar_df["batter"].tolist()
        )].sort_values("bowl_rating", ascending=False)
        bowlers = st.multiselect(
            "Bowlers",
            pure_bowl["bowler"].tolist(),
            default=pure_bowl["bowler"].tolist()[:4],
            max_selections=4,
            label_visibility="collapsed",
        )

        st.markdown(
            "<p style='color:rgba(255,255,255,0.5);font-weight:700;margin:12px 0 4px;'>Team Name</p>",
            unsafe_allow_html=True,
        )
        team_name = st.text_input("Team Name", value="My Dream XI",
                                   label_visibility="collapsed")

        st.markdown(
            "<p style='color:rgba(255,255,255,0.5);font-weight:700;margin:12px 0 4px;'>Team Color</p>",
            unsafe_allow_html=True,
        )
        team_color = st.color_picker("Pick team color", value="#00FFFF",
                                      label_visibility="collapsed")

    # Build full squad
    all_selected = ([keeper] if keeper else []) + batters + allrounders + bowlers
    total = len(all_selected)

    # Team constraint check
    team_counts = {}
    for p in all_selected:
        team = bat_df[bat_df["batter"] == p]["team"].values
        if len(team) == 0:
            team = bowl_df[bowl_df["bowler"] == p]["team"].values
        if len(team) > 0:
            t = team[0]
            team_counts[t] = team_counts.get(t, 0) + 1

    violations = {t: c for t, c in team_counts.items() if c > 4}

    st.markdown("---")
    st.markdown(f"<h3>Step 2 — Your Team ({total}/11 players)</h3>",
                unsafe_allow_html=True)

    if violations:
        for t, c in violations.items():
            st.warning(f"Too many players from {t} ({c}/4 max). Adjust your selection.")

    if total == 0:
        st.info("Select players above to build your XI.")
        return

    # ── TEAM CARD ─────────────────────────────────────────────────
    roles = {
        keeper:       ("WK",  "#FFE66D"),
        **{b: ("BAT", "#00FFFF")  for b in batters},
        **{a: ("AR",  "#4ECDC4")  for a in allrounders},
        **{bw: ("BOWL","#FF6B6B") for bw in bowlers},
    }

    player_rows = ""
    for p in all_selected:
        role_tag, role_color = roles.get(p, ("", "white"))
        b_stat = bat_df[bat_df["batter"] == p]
        bw_stat = bowl_df[bowl_df["bowler"] == p]

        if not b_stat.empty:
            stat = f"{int(b_stat.iloc[0]['runs']):,} runs | SR {b_stat.iloc[0]['sr']}"
        elif not bw_stat.empty:
            stat = f"{int(bw_stat.iloc[0]['wickets'])} wkts | Econ {bw_stat.iloc[0]['economy']}"
        else:
            stat = "—"

        player_rows += (
            f"<tr>"
            f"<td style='padding:8px 4px;color:white;font-weight:600;'>{p}</td>"
            f"<td style='padding:8px 4px;'>"
            f"<span style='background:{role_color}22;color:{role_color};"
            f"border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;'>"
            f"{role_tag}</span></td>"
            f"<td style='padding:8px 4px;color:rgba(255,255,255,0.6);font-size:13px;'>{stat}</td>"
            f"</tr>"
        )

    st.markdown(
        f"<div class='card'>"
        f"<h3 style='color:{team_color};margin-bottom:12px;'>{team_name}</h3>"
        f"<table style='width:100%;border-collapse:collapse;'>"
        f"<tr style='border-bottom:1px solid rgba(255,255,255,0.1);'>"
        f"<th style='text-align:left;color:rgba(255,255,255,0.4);font-size:11px;"
        f"text-transform:uppercase;padding:4px;'>Player</th>"
        f"<th style='text-align:left;color:rgba(255,255,255,0.4);font-size:11px;"
        f"text-transform:uppercase;padding:4px;'>Role</th>"
        f"<th style='text-align:left;color:rgba(255,255,255,0.4);font-size:11px;"
        f"text-transform:uppercase;padding:4px;'>Key Stat</th>"
        f"</tr>"
        f"{player_rows}"
        f"</table>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── TEAM RATING ───────────────────────────────────────────────
    st.markdown("<h3>Team Rating</h3>", unsafe_allow_html=True)

    if total >= 5:
        rating, radar_data = _compute_team_rating(all_selected, bat_df, bowl_df, ar_df)

        if rating >= 80:   grade, gc = "World Class", "#FFE66D"
        elif rating >= 65: grade, gc = "Strong XI",   "#4ECDC4"
        elif rating >= 50: grade, gc = "Competitive",  "#00FFFF"
        elif rating >= 35: grade, gc = "Average",      "#F7700E"
        else:              grade, gc = "Needs Work",   "#FF6B6B"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Rating", f"{rating}/100")
        c2.metric("Avg Bat Rating",  f"{round(radar_data['avg_bat_rating'], 1)}")
        c3.metric("Avg Bowl Rating", f"{round(radar_data['avg_bowl_rating'], 1)}")
        c4.metric("All Rounders",    radar_data["ar_count"])

        st.markdown(
            f"<div class='card'>"
            f"<h3 style='color:{gc};font-size:22px;'>{grade} — {rating}/100</h3>"
            f"<p style='color:rgba(255,255,255,0.6);margin-top:6px;'>"
            + (
                "Elite squad with perfect balance of batting power and bowling attack." if rating >= 80
                else "Strong team with a few gaps — could compete at the highest level." if rating >= 65
                else "Balanced side but lacks match-winners in key positions." if rating >= 50
                else "Some quality players but team balance needs work." if rating >= 35
                else "Heavy rebuilding needed — missing key role players."
            )
            + f"</p></div>",
            unsafe_allow_html=True,
        )

        # Radar chart
        col_r, col_s = st.columns([1, 1])
        with col_r:
            fig = _radar(radar_data, team_name, team_color)
            st.pyplot(fig)

        with col_s:
            # Stat breakdown
            bat_total = int(bat_df[bat_df["batter"].isin(all_selected)]["runs"].sum())
            bowl_wkts = int(bowl_df[bowl_df["bowler"].isin(all_selected)]["wickets"].sum())
            avg_econ  = round(radar_data["avg_econ"], 2)
            avg_sr    = round(radar_data["avg_sr"], 1)

            st.markdown(
                f"<div class='card'>"
                f"<p><b style='color:#00FFFF;'>Combined career runs:</b> "
                f"<span style='font-size:20px;font-weight:800;'>{bat_total:,}</span></p>"
                f"<p><b style='color:#FF6B6B;'>Combined wickets:</b> "
                f"<span style='font-size:20px;font-weight:800;'>{bowl_wkts}</span></p>"
                f"<p><b style='color:#FFE66D;'>Avg team SR:</b> "
                f"<span style='font-size:20px;font-weight:800;'>{avg_sr}</span></p>"
                f"<p><b style='color:#4ECDC4;'>Avg bowling economy:</b> "
                f"<span style='font-size:20px;font-weight:800;'>{avg_econ}</span></p>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Select at least 5 players to see team rating.")

    # ── COMPARE WITH RANDOM BEST XI ───────────────────────────────
    if st.button("Compare with All-Time Best XI", use_container_width=True):
        best_bat   = bat_df.sort_values("bat_rating",  ascending=False).head(5)["batter"].tolist()
        best_bowl  = bowl_df.sort_values("bowl_rating", ascending=False).head(4)["bowler"].tolist()
        best_ar    = ar_df.sort_values("ar_rating",    ascending=False).head(2)["batter"].tolist()
        best_keep  = keep_df.sort_values("bat_rating",  ascending=False).head(1)["batter"].tolist()
        best_xi    = best_keep + best_bat + best_ar + best_bowl

        best_rating, _ = _compute_team_rating(best_xi, bat_df, bowl_df, ar_df)
        your_rating, _ = _compute_team_rating(all_selected, bat_df, bowl_df, ar_df)
        diff            = round(your_rating - best_rating, 1)
        diff_str        = f"+{diff}" if diff >= 0 else str(diff)

        pos_color = "#4ECDC4" if diff >= 0 else "#FF6B6B"
        st.markdown(
            f"<div class='card'>"
            f"<p><b>All-Time Best XI:</b> "
            f"{', '.join(best_xi)}</p>"
            f"<p style='margin-top:10px;'>"
            f"Best XI rating: <b style='color:#FFE66D;'>{best_rating}/100</b> &nbsp;|&nbsp; "
            f"Your team: <b style='color:#00FFFF;'>{your_rating}/100</b> &nbsp;|&nbsp; "
            f"Difference: <b style='color:{pos_color};'>"
            f"{diff_str}</b></p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "<div class='card'>"
        "<p><b style='color:#00FFFF;'>Resume talking point:</b> "
        "Built a Dream XI fantasy team builder using real IPL career stats — "
        "computes team ratings from batting SR, bowling economy, and all-round balance "
        "with a radar chart visualisation. Enforces fantasy constraints (max 4 per team).</p>"
        "</div>",
        unsafe_allow_html=True,
    )
