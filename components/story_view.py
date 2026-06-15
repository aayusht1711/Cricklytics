import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# ── Constants ────────────────────────────────────────────────────
TEAM_COLORS = {
    "Mumbai Indians": "#005DA0", "Chennai Super Kings": "#F7C010",
    "Royal Challengers Bengaluru": "#EC1C24", "Royal Challengers Bangalore": "#EC1C24",
    "Kolkata Knight Riders": "#3A225D", "Rajasthan Royals": "#EA1A85",
    "Sunrisers Hyderabad": "#F7700E", "Delhi Capitals": "#0078BC",
    "Delhi Daredevils": "#0078BC", "Punjab Kings": "#ED1B24",
    "Kings XI Punjab": "#ED1B24", "Deccan Chargers": "#FDB933",
    "Gujarat Titans": "#1C4966", "Lucknow Super Giants": "#A72056",
    "Gujarat Lions": "#E8461A", "Rising Pune Supergiants": "#6F2DA8",
    "Rising Pune Supergiant": "#6F2DA8",
}
DEFAULT_COLOR = "#00FFFF"
ACCENT = "#00FFFF"
ACCENT2 = "#FFE66D"
ACCENT3 = "#FF6B6B"
TEXT_COLOR = "#e0e0e0"
AVG_FIRST_INNINGS_TOTAL = 155


# ── Styling ──────────────────────────────────────────────────────
def _inject_story_css():
    st.markdown("""
<style>
@keyframes fadeInUp {
from { opacity: 0; transform: translateY(20px); }
to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
0%, 100% { box-shadow: 0 0 8px rgba(0,229,255,0.15); }
50%      { box-shadow: 0 0 20px rgba(0,229,255,0.35); }
}
.story-header {
background: linear-gradient(135deg, rgba(0,93,160,0.35), rgba(236,28,36,0.25));
border: 1px solid rgba(255,255,255,0.1);
border-radius: 20px; padding: 32px 28px;
text-align: center; margin-bottom: 28px;
animation: fadeInUp 0.6s ease-out;
}
.story-header h2 {
font-size: 28px; font-weight: 800; color: white; margin: 0 0 6px;
font-family: "Rajdhani", sans-serif; letter-spacing: 0.5px;
}
.story-header .sub {
font-size: 14px; color: rgba(255,255,255,0.55); margin: 0;
}
.story-header .result-badge {
display: inline-block; margin-top: 12px;
background: rgba(0,229,255,0.12); border: 1px solid rgba(0,229,255,0.3);
border-radius: 8px; padding: 6px 18px;
font-size: 13px; font-weight: 700; color: #00FFFF;
}
.moment-card {
background: rgba(255,255,255,0.04);
border-radius: 12px; padding: 16px 18px;
margin-bottom: 12px;
animation: fadeInUp 0.5s ease-out;
backdrop-filter: blur(10px);
transition: transform 0.2s;
}
.moment-card:hover { transform: translateX(4px); }
.moment-title { font-size: 14px; font-weight: 700; color: white; margin: 0 0 4px; }
.moment-detail { font-size: 12px; color: rgba(255,255,255,0.55); margin: 0; }
.moment-prob { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 4px; }
.verdict-card {
background: linear-gradient(135deg, rgba(255,230,109,0.08), rgba(0,229,255,0.06));
border: 1px solid rgba(255,255,255,0.1);
border-left: 5px solid #FFE66D;
border-radius: 16px; padding: 28px 24px;
margin-top: 24px;
animation: fadeInUp 0.7s ease-out, pulseGlow 3s infinite;
}
.verdict-card h3 {
color: #FFE66D; margin: 0 0 12px; font-size: 20px; font-weight: 800;
}
.verdict-card p {
color: rgba(255,255,255,0.8); font-size: 15px; line-height: 1.8; margin: 0;
}
.scorecard-container {
background: rgba(255,255,255,0.04);
border: 1px solid rgba(255,255,255,0.08);
border-radius: 14px; padding: 20px;
margin-bottom: 10px;
}
.scorecard-title {
font-size: 15px; font-weight: 700; margin: 0 0 14px;
padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08);
}
.sc-row {
display: flex; justify-content: space-between; align-items: center;
padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.sc-name { font-size: 13px; color: rgba(255,255,255,0.85); font-weight: 600; }
.sc-stat  { font-size: 13px; color: rgba(255,255,255,0.6); }
.sc-stat b { color: white; }
</style>
""", unsafe_allow_html=True)


# ── Win Probability Engine ───────────────────────────────────────
def _sigmoid(x):
    """Numerically stable sigmoid."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    else:
        ez = math.exp(x)
        return ez / (1.0 + ez)


def _calc_win_prob_innings1(runs_scored, balls_bowled, wickets_lost):
    """
Innings-1 win probability for the batting team.
Estimates projected total via current run rate, adjusts for wickets,
then uses sigmoid to compare against average T20 first-innings score.
"""
    if balls_bowled <= 0:
        return 0.50
    crr = runs_scored / (balls_bowled / 6)
    balls_remaining = max(120 - balls_bowled, 0)
    wicket_penalty = wickets_lost * 3.5
    projected = runs_scored + (crr * (balls_remaining / 6)) - wicket_penalty
    x = (projected - AVG_FIRST_INNINGS_TOTAL) / 25.0
    return _sigmoid(x)


def _calc_win_prob_innings2(runs_scored, target, balls_remaining, wickets_lost):
    """
Innings-2 chase win probability for the batting team.
Uses required run rate and wickets in hand in a logistic model.
"""
    if runs_scored >= target:
        return 1.0
    if balls_remaining <= 0 or wickets_lost >= 10:
        return 0.0
    runs_required = target - runs_scored
    required_rr = runs_required / (balls_remaining / 6) if balls_remaining > 0 else 99.0
    wickets_in_hand = 10 - wickets_lost
    x = (wickets_in_hand * 0.5) - (required_rr * 0.3) + 1.5
    return _sigmoid(x)


@st.cache_data
def _compute_win_probability(match_df):
    """
Compute ball-by-ball win probability for the batting team in innings 1.
Returns a DataFrame with columns: ball_num, over, ball, innings,
runs_scored, wickets_lost, win_prob_batting, batter, bowler,
runs_this_ball, wicket_this_ball, batting_team.
Win prob is from the perspective of the team batting first.
"""
    match_df = match_df.sort_values(["innings", "over", "ball"]).reset_index(drop=True)

    innings1 = match_df[match_df["innings"] == 1]
    innings2 = match_df[match_df["innings"] == 2]

    # Innings 1 total (target for innings 2)
    inn1_total = int(innings1["runs_total"].sum()) if len(innings1) > 0 else 0
    target = inn1_total + 1

    batting_team_1 = innings1["batting_team"].iloc[0] if len(innings1) > 0 else "Team A"
    batting_team_2 = innings2["batting_team"].iloc[0] if len(innings2) > 0 else "Team B"

    records = []
    ball_num = 0

    # ── Innings 1 ────────────────────────────────────────────────
    cum_runs = 0
    cum_wickets = 0
    cum_balls = 0
    for _, row in innings1.iterrows():
        cum_runs += int(row["runs_total"])
        is_valid = int(row.get("valid_ball", 1))
        cum_balls += is_valid
        wicket_fell = 1 if pd.notna(row.get("wicket_kind")) and str(row.get("wicket_kind")) != "" and str(row.get("wicket_kind")).lower() != "nan" else 0
        bowler_wkt = int(row.get("bowler_wicket", 0)) if pd.notna(row.get("bowler_wicket")) else 0
        cum_wickets += wicket_fell
        ball_num += 1

        wp = _calc_win_prob_innings1(cum_runs, cum_balls, cum_wickets)

        records.append({
            "ball_num": ball_num,
            "over": int(row["over"]),
            "ball": int(row["ball"]),
            "innings": 1,
            "cum_runs": cum_runs,
            "cum_wickets": cum_wickets,
            "win_prob_bat1": wp,
            "batter": row.get("batter", ""),
            "bowler": row.get("bowler", ""),
            "runs_this_ball": int(row["runs_total"]),
            "batter_runs": int(row.get("runs_batter", 0)),
            "wicket_this_ball": wicket_fell,
            "wicket_kind": str(row.get("wicket_kind", "")),
            "player_dismissed": str(row.get("player_dismissed", "")),
            "batting_team": batting_team_1,
        })

    # ── Innings 2 ────────────────────────────────────────────────
    cum_runs_2 = 0
    cum_wickets_2 = 0
    cum_balls_2 = 0
    total_balls_inn2 = 120
    for _, row in innings2.iterrows():
        cum_runs_2 += int(row["runs_total"])
        is_valid = int(row.get("valid_ball", 1))
        cum_balls_2 += is_valid
        wicket_fell = 1 if pd.notna(row.get("wicket_kind")) and str(row.get("wicket_kind")) != "" and str(row.get("wicket_kind")).lower() != "nan" else 0
        # bowler_wkt = int(row.get("bowler_wicket", 0)) if pd.notna(row.get("bowler_wicket")) else 0
        cum_wickets_2 += wicket_fell
        ball_num += 1

        balls_rem = max(total_balls_inn2 - cum_balls_2, 0)
        wp_chase = _calc_win_prob_innings2(cum_runs_2, target, balls_rem, cum_wickets_2)
        # From batting-first team's perspective: 1 - chase probability
        wp_bat1 = 1.0 - wp_chase

        records.append({
            "ball_num": ball_num,
            "over": int(row["over"]),
            "ball": int(row["ball"]),
            "innings": 2,
            "cum_runs": cum_runs_2,
            "cum_wickets": cum_wickets_2,
            "win_prob_bat1": wp_bat1,
            "batter": row.get("batter", ""),
            "bowler": row.get("bowler", ""),
            "runs_this_ball": int(row["runs_total"]),
            "batter_runs": int(row.get("runs_batter", 0)),
            "wicket_this_ball": wicket_fell,
            "wicket_kind": str(row.get("wicket_kind", "")),
            "player_dismissed": str(row.get("player_dismissed", "")),
            "batting_team": batting_team_2,
        })

    return pd.DataFrame(records), batting_team_1, batting_team_2, target


# ── Key Moment Detection ────────────────────────────────────────
def _detect_key_moments(wp_df):
    """
Identify key moments based on:
- Wickets (especially in death overs 16-20)
- Win probability shift > 5% on a single ball
- Over yielding 15+ runs
- Six in the final 2 overs
Returns a list of dicts with moment details.
"""
    moments = []
    seen_overs = set()

    prev_wp = 0.5
    for i, row in wp_df.iterrows():
        wp = row["win_prob_bat1"]
        shift = abs(wp - prev_wp) * 100
        over_num = int(row["over"]) + 1  # 1-indexed display

        # ── Wicket ───────────────────────────────────────────────
        if row["wicket_this_ball"] == 1:
            severity = "high" if over_num >= 16 else "medium"
            dismissed = row["player_dismissed"] if row["player_dismissed"] not in ("", "nan") else "a batter"
            kind = row["wicket_kind"] if row["wicket_kind"] not in ("", "nan") else "dismissed"
            emoji = "🔴"
            moments.append({
                "ball_num": row["ball_num"],
                "innings": row["innings"],
                "over": over_num,
                "ball": row["ball"],
                "type": "wicket",
                "severity": severity,
                "color": ACCENT3,
                "emoji": emoji,
                "title": f"WICKET! {dismissed} — {kind}",
                "detail": f"Bowler: {row['bowler']} | Over {over_num}.{row['ball']} | Inn {row['innings']}",
                "wp_shift": shift,
                "wp_after": wp,
            })

        # ── Win prob shift > 5% ──────────────────────────────────
        elif shift > 5.0:
            direction = "towards" if wp > prev_wp else "away from"
            emoji = "⚡"
            moments.append({
                "ball_num": row["ball_num"],
                "innings": row["innings"],
                "over": over_num,
                "ball": row["ball"],
                "type": "momentum",
                "severity": "high" if shift > 10 else "medium",
                "color": ACCENT2,
                "emoji": emoji,
                "title": f"Momentum Shift! {shift:.1f}% swing",
                "detail": f"{row['batter']} hit {row['batter_runs']} off {row['bowler']} | Over {over_num}.{row['ball']}",
                "wp_shift": shift,
                "wp_after": wp,
            })

        # ── Six in final 2 overs ────────────────────────────────
        elif row["batter_runs"] == 6 and over_num >= 19:
            emoji = "💥"
            moments.append({
                "ball_num": row["ball_num"],
                "innings": row["innings"],
                "over": over_num,
                "ball": row["ball"],
                "type": "big_hit",
                "severity": "medium",
                "color": ACCENT,
                "emoji": emoji,
                "title": f"SIX! {row['batter']} launches it!",
                "detail": f"Off {row['bowler']} | Over {over_num}.{row['ball']} | Inn {row['innings']}",
                "wp_shift": shift,
                "wp_after": wp,
            })

        prev_wp = wp

    # ── Big overs (15+ runs) ─────────────────────────────────────
    for inn in [1, 2]:
        inn_df = wp_df[wp_df["innings"] == inn]
        if inn_df.empty:
            continue
        over_runs = inn_df.groupby("over").agg(
            total_runs=("runs_this_ball", "sum"),
            first_ball_num=("ball_num", "first"),
            batting_team=("batting_team", "first"),
            bowler=("bowler", "first"),
        ).reset_index()
        big_overs = over_runs[over_runs["total_runs"] >= 15]
        for _, ov_row in big_overs.iterrows():
            over_display = int(ov_row["over"]) + 1
            key = (inn, over_display)
            if key not in seen_overs:
                seen_overs.add(key)
                # Get wp at start and end of over
                ov_balls = inn_df[inn_df["over"] == ov_row["over"]]
                wp_start = ov_balls["win_prob_bat1"].iloc[0] if len(ov_balls) > 0 else 0.5
                wp_end = ov_balls["win_prob_bat1"].iloc[-1] if len(ov_balls) > 0 else 0.5
                wp_shift_ov = abs(wp_end - wp_start) * 100
                moments.append({
                    "ball_num": int(ov_row["first_ball_num"]),
                    "innings": inn,
                    "over": over_display,
                    "ball": 1,
                    "type": "big_over",
                    "severity": "high" if int(ov_row["total_runs"]) >= 20 else "medium",
                    "color": "#4ECDC4",
                    "emoji": "🔥",
                    "title": f"Big Over! {int(ov_row['total_runs'])} runs in Over {over_display}",
                    "detail": f"Bowled by {ov_row['bowler']} | Inn {inn}",
                    "wp_shift": wp_shift_ov,
                    "wp_after": wp_end,
                })

    # Sort by ball number and deduplicate close moments
    moments.sort(key=lambda m: m["ball_num"])

    # Keep only the top 12 most impactful moments to avoid clutter
    if len(moments) > 12:
        moments.sort(key=lambda m: m["wp_shift"], reverse=True)
        moments = moments[:12]
        moments.sort(key=lambda m: m["ball_num"])

    return moments


# ── Match Verdict Generator ──────────────────────────────────────
def _generate_verdict(match_info, wp_df, bat_team1, bat_team2):
    """Generate template-based match verdict text."""
    winner = str(match_info.get("match_won_by", ""))
    win_outcome = str(match_info.get("win_outcome", ""))
    potm = str(match_info.get("player_of_match", ""))

    if not winner or winner == "nan":
        return "Match result data unavailable."

    loser = bat_team2 if winner == bat_team1 else bat_team1

    # Determine match drama level from win probability swings
    if wp_df is not None and len(wp_df) > 1:
        wp_vals = wp_df["win_prob_bat1"].values
        max_swing = 0
        for i in range(1, len(wp_vals)):
            swing = abs(wp_vals[i] - wp_vals[i - 1])
            if swing > max_swing:
                max_swing = swing

        min_wp = wp_vals.min()
        max_wp = wp_vals.max()
        range_wp = max_wp - min_wp

        if range_wp > 0.6 or max_swing > 0.15:
            drama = "thrilling"
        elif range_wp > 0.35:
            drama = "exciting"
        elif range_wp > 0.2:
            drama = "comfortable"
        else:
            drama = "dominant"
    else:
        drama = "competitive"

    # Build the verdict text
    outcome_text = f"by {win_outcome}" if win_outcome and win_outcome != "nan" else ""

    verdict = f"In a {drama} contest, {winner} defeated {loser} {outcome_text}."

    if potm and potm != "nan":
        verdict += f" {potm}'s match-winning performance earned them the Player of the Match award."

    # Add flavor based on drama level
    if drama == "thrilling":
        verdict += " The match swung back and forth with dramatic momentum shifts that kept fans on the edge of their seats."
    elif drama == "exciting":
        verdict += " Both teams put up a strong fight, making for an entertaining encounter."
    elif drama == "dominant":
        verdict += " It was a clinical display of cricket with the outcome never seriously in doubt."

    return verdict


# ── Scorecard Builder ────────────────────────────────────────────
@st.cache_data
def _build_scorecard(match_df):
    """Build top-3 batters and bowlers for each innings."""
    scorecards = {}
    for inn in [1, 2]:
        inn_df = match_df[match_df["innings"] == inn]
        if inn_df.empty:
            continue

        team = inn_df["batting_team"].iloc[0]

        # Top batters
        bat = inn_df.groupby("batter").agg(
            runs=("runs_batter", "sum"),
            balls=("valid_ball", "sum"),
            fours=("runs_batter", lambda x: (x == 4).sum()),
            sixes=("runs_batter", lambda x: (x == 6).sum()),
        ).reset_index()
        bat["sr"] = (bat["runs"] / bat["balls"] * 100).round(1).fillna(0)
        top_bat = bat.sort_values("runs", ascending=False).head(3)

        # Top bowlers
        bowling_team_df = match_df[(match_df["innings"] == inn)]
        bowl = bowling_team_df.groupby("bowler").agg(
            wickets=("bowler_wicket", "sum"),
            runs_conceded=("runs_total", "sum"),
            balls=("valid_ball", "sum"),
        ).reset_index()
        bowl = bowl[bowl["balls"] > 0]
        bowl["econ"] = (bowl["runs_conceded"] / bowl["balls"] * 6).round(2)
        bowl["overs_str"] = bowl["balls"].apply(lambda b: f"{b // 6}.{b % 6}")
        top_bowl = bowl.sort_values("wickets", ascending=False).head(3)

        scorecards[inn] = {
            "team": team,
            "total_runs": int(inn_df["runs_total"].sum()),
            "total_wickets": int(inn_df["wicket_kind"].dropna().apply(
                lambda x: 1 if str(x) not in ("", "nan") else 0
            ).sum()),
            "total_balls": int(inn_df["valid_ball"].sum()),
            "top_batters": top_bat,
            "top_bowlers": top_bowl,
        }

    return scorecards


# ── Plotly Win Probability Chart ─────────────────────────────────
def _plot_win_prob(wp_df, bat_team1, bat_team2, key_moments):
    """Create a full-width Plotly area chart for win probability timeline."""
    color1 = TEAM_COLORS.get(bat_team1, ACCENT)
    color2 = TEAM_COLORS.get(bat_team2, ACCENT3)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Innings 1 data
    inn1 = wp_df[wp_df["innings"] == 1]
    inn2 = wp_df[wp_df["innings"] == 2]

    # Team 1 win probability area (above 0.5)
    fig.add_trace(go.Scatter(
        x=wp_df["ball_num"],
        y=wp_df["win_prob_bat1"] * 100,
        mode="lines",
        line=dict(color=color1, width=2.5),
        fill="tozeroy",
        fillcolor=f"rgba({int(color1[1:3], 16)},{int(color1[3:5], 16)},{int(color1[5:7], 16)},0.15)",
        name=bat_team1,
        hovertemplate=(
            "<b>Ball %{x}</b><br>"
            f"{bat_team1} Win: " + "%{y:.1f}%<br>"
            f"{bat_team2} Win: " + "%{customdata:.1f}%"
            "<extra></extra>"
        ),
        customdata=[(1 - wp) * 100 for wp in wp_df["win_prob_bat1"]],
    ), secondary_y=False)

    # Worm for innings 1
    if len(inn1) > 0:
        fig.add_trace(go.Scatter(
            x=inn1["ball_num"],
            y=inn1["cum_runs"],
            mode="lines",
            line=dict(color=color1, width=3, dash="solid"),
            name=f"{bat_team1} Runs (Worm)",
            hovertemplate="<b>Ball %{x}</b><br>Runs: %{y}<extra></extra>",
        ), secondary_y=True)

    # Worm for innings 2
    if len(inn2) > 0:
        fig.add_trace(go.Scatter(
            x=inn2["ball_num"],
            y=inn2["cum_runs"],
            mode="lines",
            line=dict(color=color2, width=3, dash="solid"),
            name=f"{bat_team2} Runs (Worm)",
            hovertemplate="<b>Ball %{x}</b><br>Runs: %{y}<extra></extra>",
        ), secondary_y=True)

    # 50% baseline
    fig.add_hline(
        y=50, line_dash="dot",
        line_color="rgba(255,255,255,0.2)", line_width=1,
    )

    # Innings separator
    if len(inn1) > 0 and len(inn2) > 0:
        separator_x = inn1["ball_num"].max() + 0.5
        fig.add_vline(
            x=separator_x, line_dash="dash",
            line_color="rgba(255,255,255,0.25)", line_width=1,
            annotation_text="Innings Break",
            annotation_position="top",
            annotation_font_color="rgba(255,255,255,0.5)",
            annotation_font_size=11,
        )

    # Key moment markers
    for m in key_moments:
        if m["type"] == "wicket":
            marker_color = ACCENT3
            marker_symbol = "x"
            marker_size = 10
        elif m["type"] == "momentum":
            marker_color = ACCENT2
            marker_symbol = "diamond"
            marker_size = 9
        elif m["type"] == "big_over":
            marker_color = "#4ECDC4"
            marker_symbol = "triangle-up"
            marker_size = 10
        else:
            marker_color = ACCENT
            marker_symbol = "star"
            marker_size = 9

        fig.add_trace(go.Scatter(
            x=[m["ball_num"]],
            y=[m["wp_after"] * 100],
            mode="markers",
            marker=dict(color=marker_color, size=marker_size, symbol=marker_symbol,
                        line=dict(width=1, color="white")),
            name=m["title"][:30],
            hovertemplate=f"<b>{m['emoji']} {m['title']}</b><br>{m['detail']}<extra></extra>",
            showlegend=False,
        ))

    # Team annotations
    fig.add_annotation(
        x=0.02, y=0.95, xref="paper", yref="paper",
        text=f"⬆ {bat_team1}", showarrow=False,
        font=dict(color=color1, size=12, family="Rajdhani, sans-serif"),
    )
    fig.add_annotation(
        x=0.02, y=0.05, xref="paper", yref="paper",
        text=f"⬇ {bat_team2}", showarrow=False,
        font=dict(color=color2, size=12, family="Rajdhani, sans-serif"),
    )

    fig.update_layout(
        title=dict(
            text="📈 Win Probability Timeline",
            font=dict(size=18, color="white", family="Rajdhani, sans-serif"),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT_COLOR,
        xaxis=dict(
            title="Ball Number",
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            showline=False,
        ),
        yaxis=dict(
            title="Win Probability (%)",
            range=[0, 100],
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            showline=False,
            ticksuffix="%",
        ),
        yaxis2=dict(
            title="Cumulative Runs (Worm)",
            range=[0, max(wp_df["cum_runs"].max() + 10 if not wp_df.empty else 200, 200)],
            showgrid=False,
            zeroline=False,
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.18,
            xanchor="center", x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
        margin=dict(l=50, r=20, t=60, b=60),
        height=420,
        hovermode="x unified",
    )

    return fig


# ── Render Helpers ───────────────────────────────────────────────
def _render_header(match_info, bat_team1, bat_team2):
    """Render the cinematic match header card."""
    color1 = TEAM_COLORS.get(bat_team1, ACCENT)
    color2 = TEAM_COLORS.get(bat_team2, ACCENT3)
    date_str = str(match_info.get("date", ""))
    venue = str(match_info.get("venue", ""))
    city = str(match_info.get("city", ""))
    winner = str(match_info.get("match_won_by", ""))
    outcome = str(match_info.get("win_outcome", ""))
    potm = str(match_info.get("player_of_match", ""))
    stage = str(match_info.get("stage", ""))

    result_text = ""
    if winner and winner != "nan":
        result_text = f"{winner} won"
        if outcome and outcome != "nan":
            result_text += f" by {outcome}"

    stage_badge = ""
    if stage and stage != "nan" and stage.lower() not in ("group", "league"):
        stage_badge = f"<span style='background:rgba(255,107,107,0.15);color:#FF6B6B;font-size:11px;font-weight:700;padding:2px 10px;border-radius:4px;margin-left:8px;text-transform:uppercase;'>{stage}</span>"

    potm_html = ""
    if potm and potm != "nan":
        potm_html = f"<div style='margin-top:8px;font-size:13px;color:rgba(255,255,255,0.55);'>⭐ Player of the Match: <b style=\"color:#FFE66D;\">{potm}</b></div>"

    location = city if city and city != "nan" else ""
    if venue and venue != "nan":
        location = f"{venue}, {location}" if location else venue

    st.markdown(f"""
<div class="story-header">
<div style="font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">
🎬 Match Story Mode {stage_badge}
</div>
<h2>
<span style="color:{color1};">{bat_team1}</span>
<span style="color:rgba(255,255,255,0.3);font-size:18px;"> vs </span>
<span style="color:{color2};">{bat_team2}</span>
</h2>
<p class="sub">📍 {location} &nbsp;·&nbsp; 📅 {date_str}</p>
{f'<div class="result-badge">{result_text}</div>' if result_text else ''}
{potm_html}
</div>
""", unsafe_allow_html=True)


def _render_key_moments(moments):
    """Render the vertical timeline of key moments."""
    if not moments:
        st.info("No significant key moments detected for this match.")
        return

    st.markdown("""
<div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:20px;
border-left:4px solid #00e5ff;backdrop-filter:blur(10px);margin-bottom:16px;'>
<h3 style='color:#FFE66D;margin:0 0 4px;font-size:18px;'>⚡ Key Moments</h3>
<p style='color:rgba(255,255,255,0.45);margin:0;font-size:12px;'>
Pivotal deliveries that shaped the match outcome
</p>
</div>
""", unsafe_allow_html=True)

    for m in moments:
        severity_border = "4px" if m["severity"] == "high" else "3px"
        wp_display = f"{m['wp_after'] * 100:.0f}%"
        shift_text = f"±{m['wp_shift']:.1f}% swing" if m["wp_shift"] > 0 else ""

        st.markdown(f"""
<div class="moment-card" style="border-left:{severity_border} solid {m['color']};">
<div style="display:flex;justify-content:space-between;align-items:center;">
<div>
<p class="moment-title">{m['emoji']} {m['title']}</p>
<p class="moment-detail">{m['detail']}</p>
</div>
<div style="text-align:right;min-width:80px;">
<div style="font-size:16px;font-weight:800;color:{m['color']};">{wp_display}</div>
<div style="font-size:10px;color:rgba(255,255,255,0.35);">{shift_text}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


def _render_scorecard(scorecards, bat_team1, bat_team2):
    """Render the two-column scorecard with top 3 batters and bowlers."""
    st.markdown("""
<div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:20px;
border-left:4px solid #00e5ff;backdrop-filter:blur(10px);margin-bottom:16px;'>
<h3 style='color:#FFE66D;margin:0 0 4px;font-size:18px;'>📋 Match Scorecard</h3>
<p style='color:rgba(255,255,255,0.45);margin:0;font-size:12px;'>
Top performers from each innings
</p>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    for inn_num, col in [(1, col1), (2, col2)]:
        with col:
            if inn_num not in scorecards:
                st.caption(f"Innings {inn_num} data unavailable")
                continue

            sc = scorecards[inn_num]
            team = sc["team"]
            t_color = TEAM_COLORS.get(team, ACCENT)
            total_overs = f"{sc['total_balls'] // 6}.{sc['total_balls'] % 6}"

            # Team header
            st.markdown(f"""
<div class="scorecard-container" style="border-top:3px solid {t_color};">
<div class="scorecard-title" style="color:{t_color};">
{team} &nbsp;
<span style="color:white;font-size:18px;font-weight:800;">
{sc['total_runs']}/{sc['total_wickets']}
</span>
<span style="color:rgba(255,255,255,0.4);font-size:12px;">
({total_overs} ov)
</span>
</div>
""", unsafe_allow_html=True)

            # Top batters
            st.markdown("<div style='font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;font-weight:700;'>🏏 Top Batters</div>", unsafe_allow_html=True)
            for _, b in sc["top_batters"].iterrows():
                sr_val = b["sr"] if pd.notna(b["sr"]) else 0
                st.markdown(f"""
<div class="sc-row">
<span class="sc-name">{b['batter']}</span>
<span class="sc-stat"><b>{int(b['runs'])}</b> ({int(b['balls'])}) &nbsp; SR: {sr_val} &nbsp; 4s:{int(b['fours'])} 6s:{int(b['sixes'])}</span>
</div>
""", unsafe_allow_html=True)

            # Top bowlers
            st.markdown("<div style='font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin:12px 0 6px;font-weight:700;'>🎯 Top Bowlers</div>", unsafe_allow_html=True)
            for _, b in sc["top_bowlers"].iterrows():
                st.markdown(f"""
<div class="sc-row">
<span class="sc-name">{b['bowler']}</span>
<span class="sc-stat"><b>{int(b['wickets'])}</b>/{int(b['runs_conceded'])} &nbsp; ({b['overs_str']} ov) &nbsp; Econ: {b['econ']}</span>
</div>
""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


def _render_verdict(verdict_text):
    """Render the match verdict card."""
    st.markdown(f"""
<div class="verdict-card">
<h3>🏆 Match Verdict</h3>
<p>{verdict_text}</p>
</div>
""", unsafe_allow_html=True)


# ── Main Entry Point ─────────────────────────────────────────────
def show_story_view(data):
    """Match Story Mode — cinematic match replay with win probability,
key moments, scorecard, and AI-generated verdict."""

    _inject_story_css()

    st.markdown("""
<div style="text-align:center;margin-bottom:6px;">
<span style="font-size:32px;">🎬</span>
<h2 style="color:white;margin:4px 0 2px;font-family:'Rajdhani',sans-serif;font-weight:800;
background:linear-gradient(90deg,#00FFFF,#FFE66D);-webkit-background-clip:text;
-webkit-text-fill-color:transparent;font-size:30px;">
Match Story Mode
</h2>
<p style="color:rgba(255,255,255,0.45);font-size:13px;margin:0;">
Relive every twist and turn — ball by ball
</p>
</div>
""", unsafe_allow_html=True)

    try:
        # ── Season & Match Selection ─────────────────────────────
        if "season" not in data.columns or "match_id" not in data.columns:
            st.error("Dataset is missing required columns (season, match_id).")
            return

        all_seasons = sorted(data["season"].dropna().unique(), reverse=True)
        if not all_seasons:
            st.warning("No seasons found in the dataset.")
            return

        sel_col1, sel_col2 = st.columns([1, 3])
        with sel_col1:
            selected_season = st.selectbox("📅 Season", all_seasons, key="story_season")

        season_df = data[data["season"] == selected_season]

        # Build match labels
        match_info_df = season_df.drop_duplicates("match_id")
        match_options = {}
        for _, row in match_info_df.iterrows():
            mid = row["match_id"]
            date_val = str(row.get("date", ""))[:10]
            team1 = str(row.get("batting_team", ""))
            # Find the other team
            teams_in_match = season_df[season_df["match_id"] == mid]["batting_team"].unique()
            team2 = [t for t in teams_in_match if t != team1]
            team2_str = team2[0] if team2 else "Unknown"
            potm = str(row.get("player_of_match", ""))
            potm_str = f" — {potm} ★" if potm and potm != "nan" else ""
            label = f"{date_val} | {team1} vs {team2_str}{potm_str}"
            match_options[label] = mid

        if not match_options:
            st.warning("No matches found for this season.")
            return

        with sel_col2:
            selected_label = st.selectbox(
                "🏏 Select Match", list(match_options.keys()), key="story_match"
            )

        selected_match_id = match_options[selected_label]
        match_df = season_df[season_df["match_id"] == selected_match_id].copy()

        if match_df.empty:
            st.warning("No ball-by-ball data found for this match.")
            return

        # ── Extract match metadata ───────────────────────────────
        meta_row = match_df.iloc[0]
        match_meta = {
            "date": meta_row.get("date", ""),
            "venue": meta_row.get("venue", ""),
            "city": meta_row.get("city", ""),
            "match_won_by": meta_row.get("match_won_by", ""),
            "win_outcome": meta_row.get("win_outcome", ""),
            "player_of_match": meta_row.get("player_of_match", ""),
            "stage": meta_row.get("stage", ""),
        }

        # ── Compute win probability ──────────────────────────────
        wp_df, bat_team1, bat_team2, target = _compute_win_probability(match_df)

        if wp_df.empty:
            st.warning("Could not compute win probability for this match.")
            return

        # ── Render header ────────────────────────────────────────
        _render_header(match_meta, bat_team1, bat_team2)

        # ── Win Probability Chart ────────────────────────────────
        key_moments = _detect_key_moments(wp_df)
        fig = _plot_win_prob(wp_df, bat_team1, bat_team2, key_moments)
        st.plotly_chart(fig, use_container_width=True)

        # ── Key Moments Timeline ─────────────────────────────────
        _render_key_moments(key_moments)

        # ── Scorecard ────────────────────────────────────────────
        scorecards = _build_scorecard(match_df)
        _render_scorecard(scorecards, bat_team1, bat_team2)

        # ── Match Verdict ────────────────────────────────────────
        verdict = _generate_verdict(match_meta, wp_df, bat_team1, bat_team2)
        _render_verdict(verdict)

        # ── Footer ───────────────────────────────────────────────
        st.markdown("""
<div style='text-align:center;margin-top:28px;font-size:11px;color:rgba(255,255,255,0.25);'>
Win probability is a simplified model based on run rate, wickets, and required rate.
Not intended as a predictive tool — purely for storytelling.
</div>
""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Something went wrong rendering the match story: {str(e)}")
        st.caption("Try selecting a different match — some matches may have incomplete data.")
