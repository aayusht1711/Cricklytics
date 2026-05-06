import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

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
def _compute_player_profile(data, player):
    df = data[data["batter"] == player].copy()
    if df.empty:
        return None

    runs         = int(df["runs_batter"].sum())
    balls        = int(df["balls_faced"].sum()) if "balls_faced" in df.columns else len(df)
    sr           = round(runs / balls * 100, 2) if balls > 0 else 0
    fours        = int((df["runs_batter"] == 4).sum())
    sixes        = int((df["runs_batter"] == 6).sum())
    dots         = int((df["runs_batter"] == 0).sum())
    dot_pct      = round(dots / balls * 100, 1) if balls > 0 else 0
    boundary_pct = round((fours + sixes) / balls * 100, 1) if balls > 0 else 0
    dismissals   = int(df["player_dismissed"].notna().sum()) if "player_dismissed" in df.columns else 0
    avg          = round(runs / dismissals, 2) if dismissals > 0 else runs
    seasons      = df["season"].astype(str).nunique()
    primary_team = df["batting_team"].value_counts().index[0] if len(df) > 0 else ""

    
    df2 = df.copy()
    df2["phase"] = pd.cut(df2["over"], bins=[-1, 5, 14, 19],
                          labels=["Powerplay", "Middle", "Death"])
    bcol = "balls_faced" if "balls_faced" in df2.columns else "runs_batter"
    phase = df2.groupby("phase", observed=True).agg(
        runs=("runs_batter", "sum"), balls=(bcol, "sum")
    )
    pp_sr     = round(phase.loc["Powerplay", "runs"] / max(phase.loc["Powerplay", "balls"], 1) * 100, 1)
    mid_sr    = round(phase.loc["Middle", "runs"]    / max(phase.loc["Middle", "balls"],    1) * 100, 1)
    death_sr  = round(phase.loc["Death", "runs"]     / max(phase.loc["Death", "balls"],     1) * 100, 1)

    # Knockout vs league
    ko_stages = ["Final","Semi Final","Qualifier 1","Qualifier 2","Eliminator","Elimination Final"]
    ko_df     = df[df["stage"].isin(ko_stages)]
    ko_runs   = int(ko_df["runs_batter"].sum())
    ko_balls  = int(ko_df["balls_faced"].sum()) if "balls_faced" in ko_df.columns else len(ko_df)
    ko_sr     = round(ko_runs / ko_balls * 100, 1) if ko_balls > 0 else 0

    # Match-level 50s and 100s
    match_runs  = df.groupby("match_id")["runs_batter"].sum()
    fifties     = int(((match_runs >= 50) & (match_runs < 100)).sum())
    hundreds    = int((match_runs >= 100).sum())
    best_score  = int(match_runs.max())

    return {
        "player":       player,
        "team":         primary_team,
        "seasons":      seasons,
        "runs":         runs,
        "balls":        balls,
        "sr":           sr,
        "avg":          avg,
        "fours":        fours,
        "sixes":        sixes,
        "dot_pct":      dot_pct,
        "boundary_pct": boundary_pct,
        "pp_sr":        pp_sr,
        "mid_sr":       mid_sr,
        "death_sr":     death_sr,
        "ko_runs":      ko_runs,
        "ko_sr":        ko_sr,
        "fifties":      fifties,
        "hundreds":     hundreds,
        "best_score":   best_score,
        "dismissals":   dismissals,
    }


def _build_scouting_prompt(profile):
    p = profile
    return f"""You are a professional cricket analyst and talent scout writing for an IPL franchise.
Write a sharp, insightful 3-paragraph scouting report for {p['player']} based on these real IPL stats:

CAREER STATS:
- Total Runs: {p['runs']:,} | Balls: {p['balls']:,} | Strike Rate: {p['sr']} | Average: {p['avg']}
- Fours: {p['fours']} | Sixes: {p['sixes']} | Best Score: {p['best_score']}
- 50s: {p['fifties']} | 100s: {p['hundreds']} | Seasons: {p['seasons']}
- Dot Ball %: {p['dot_pct']}% | Boundary %: {p['boundary_pct']}%

PHASE BREAKDOWN:
- Powerplay SR: {p['pp_sr']} | Middle Overs SR: {p['mid_sr']} | Death Overs SR: {p['death_sr']}

KNOCKOUT PERFORMANCE:
- Knockout Runs: {p['ko_runs']} | Knockout SR: {p['ko_sr']}

FORMAT:
Paragraph 1: Overall batting profile and playing style (what kind of batter are they?)
Paragraph 2: Strengths and best conditions to deploy them
Paragraph 3: Weaknesses, concerns, and verdict — would you buy them at IPL auction?

Write like a professional scout — specific, data-driven, no fluff. Reference actual numbers."""


def _call_groq(prompt, api_key):
    try:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        body    = {
            "model":    GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
            "temperature": 0.7,
        }
        resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
        data = resp.json()
        if "error" in data:
            return None, data["error"].get("message", "API error")
        return data["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, str(e)


def _radar_chart(profile):
    """5-axis radar showing player strengths."""
    categories = ["Power\n(Sixes)", "Consistency\n(Avg)", "Aggression\n(SR)",
                  "Clutch\n(KO SR)", "Reliability\n(50s+100s)"]

    # Normalize each to 0-100
    def norm(val, max_val):
        return min(100, round(val / max_val * 100, 0))

    values = [
        norm(profile["sixes"],    400),
        norm(profile["avg"],      60),
        norm(profile["sr"],       200),
        norm(profile["ko_sr"],    200),
        norm(profile["fifties"] + profile["hundreds"] * 2, 50),
    ]
    values += [values[0]]  # close the loop
    N = len(categories)

    import numpy as np
    angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    t_color = TEAM_COLORS.get(profile["team"], "#00FFFF")
    ax.plot(angles, values, color=t_color, linewidth=2)
    ax.fill(angles, values, alpha=0.2, color=t_color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color="white", fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], color="#555", fontsize=6)
    ax.spines["polar"].set_color("#333")
    ax.grid(color="#333", linewidth=0.5)
    ax.set_title(f"{profile['player']}", color="white", fontsize=11, pad=15)
    plt.tight_layout()
    return fig


def show_scouting_view(data):
    st.markdown("<h2>AI Scouting Report</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5);margin-bottom:20px;'>"
        "Select any IPL player — AI analyses their real career stats and generates "
        "a professional franchise scouting report</p>",
        unsafe_allow_html=True,
    )

    # Controls
    col_p, col_k = st.columns([3, 2])
    with col_p:
        player = st.selectbox("Select Player to Scout", sorted(data["batter"].unique()))
    with col_k:
        api_key = st.text_input("Groq API Key (free at console.groq.com)",
                                type="password",
                                placeholder="gsk_...")

    profile = _compute_player_profile(data, player)
    if profile is None:
        st.error("No data for this player.")
        return

    t_color = TEAM_COLORS.get(profile["team"], "#00FFFF")

    # Player stats card
    st.markdown(
        f"<div class='card'>"
        f"<h3 style='color:{t_color};'>{player}</h3>"
        f"<p><b>Team:</b> {profile['team']} &nbsp;|&nbsp; "
        f"<b>Seasons:</b> {profile['seasons']} &nbsp;|&nbsp; "
        f"<b>Best Score:</b> {profile['best_score']}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Runs", f"{profile['runs']:,}")
    c2.metric("Strike Rate", profile["sr"])
    c3.metric("Average", profile["avg"])
    c4.metric("Sixes", profile["sixes"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Powerplay SR", profile["pp_sr"])
    c6.metric("Middle SR",    profile["mid_sr"])
    c7.metric("Death SR",     profile["death_sr"])
    c8.metric("Knockout SR",  profile["ko_sr"])

    # Radar chart
    col_r, col_s = st.columns([1, 2])
    with col_r:
        st.markdown("<h3>Player Radar</h3>", unsafe_allow_html=True)
        fig_radar = _radar_chart(profile)
        st.pyplot(fig_radar)

    with col_s:
        st.markdown("<h3>Milestone Record</h3>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='card'>"
            f"<p>50s: <b style='color:#FFE66D;font-size:20px;'>{profile['fifties']}</b></p>"
            f"<p>100s: <b style='color:#00FFFF;font-size:20px;'>{profile['hundreds']}</b></p>"
            f"<p>Boundary %: <b style='color:#FF6B6B;font-size:20px;'>{profile['boundary_pct']}%</b></p>"
            f"<p>Dot Ball %: <b style='color:rgba(255,255,255,0.6);font-size:20px;'>{profile['dot_pct']}%</b></p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    
    st.markdown("---")
    st.markdown("<h3>AI Scouting Report</h3>", unsafe_allow_html=True)

    generate = st.button("Generate AI Scouting Report", use_container_width=True)

    if generate:
        if not api_key or len(api_key) < 8:
            st.warning("Paste your Groq API key above. Free at console.groq.com")
            return

        with st.spinner(f"Scouting {player}..."):
            prompt  = _build_scouting_prompt(profile)
            report, error = _call_groq(prompt, api_key)

        if error:
            st.error(f"API Error: {error}")
            return

        st.markdown(
            f"<div class='card'>"
            f"<p style='color:#00FFFF;font-weight:700;margin-bottom:12px;'>"
            f"SCOUTING REPORT — {player.upper()}</p>"
            f"<p style='line-height:1.9;color:rgba(255,255,255,0.85);white-space:pre-wrap;'>"
            f"{report}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.text_area("Copy report", value=report, height=200)

    
    st.markdown("---")
    st.markdown(
        "<div class='card'>"
        "<p><b style='color:#00FFFF;'>Resume talking point:</b> "
        "Built an AI-powered player scouting system combining LLM (Groq Llama 3.3 70B) "
        "with structured cricket stats — generates professional franchise scouting reports "
        "with radar charts, phase-wise analysis, and knockout performance metrics.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
