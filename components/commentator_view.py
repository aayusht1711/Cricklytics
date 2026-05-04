import streamlit as st
import pandas as pd
import json
import requests
from utils.chart_style import (
    apply_dark_style, dark_line_chart,
    DARK_BG, ACCENT, ACCENT2, ACCENT3, TEXT_COLOR,
    team_color
)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


PROVIDERS = {
    "🚀 Groq — Llama 3.3 70B  (fastest · 14,400 req/day free)": {
        "signup": "https://console.groq.com",
        "url":    "https://api.groq.com/openai/v1/chat/completions",
        "model":  "llama-3.3-70b-versatile",
        "fmt":    "openai",
    },
    "🌟 Google Gemini Flash  (1,500 req/day free)": {
        "signup": "https://aistudio.google.com/apikey",
        "url":    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "model":  "gemini-2.0-flash",
        "fmt":    "gemini",
    },
    "🔀 OpenRouter — Llama free  (50 req/day free)": {
        "signup": "https://openrouter.ai",
        "url":    "https://openrouter.ai/api/v1/chat/completions",
        "model":  "meta-llama/llama-3.3-70b-instruct:free",
        "fmt":    "openai",
    },
}


# ════════════════════════════════════════════════════════════════
# DATA HELPERS
# ════════════════════════════════════════════════════════════════
@st.cache_data
def get_match_list(data):
    """Return a readable list of matches for the selector."""
    matches = (
        data.drop_duplicates("match_id")[[
            "match_id", "batting_team", "bowling_team",
            "date", "season", "venue", "match_won_by",
            "win_outcome", "player_of_match", "stage"
        ]]
        .dropna(subset=["match_won_by"])
        .sort_values("date", ascending=False)
        .reset_index(drop=True)
    )
    # Readable label
    matches["label"] = (
        matches["season"].astype(str) + " | "
        + matches["batting_team"].str[:12] + " vs "
        + matches["bowling_team"].str[:12] + " — "
        + matches["venue"].str.split(",").str[0].str[:20]
    )
    return matches


def _build_match_summary(data, match_id):
    """Build a structured dict of match events to feed Claude."""
    md = data[data["match_id"] == match_id].sort_values(["innings", "over", "ball"])
    if md.empty:
        return None

    meta = md.iloc[0]
    result = {}

    result["meta"] = {
        "team1":          meta["batting_team"],
        "team2":          meta["bowling_team"],
        "venue":          meta["venue"],
        "date":           str(meta["date"]),
        "season":         str(meta["season"]),
        "winner":         meta["match_won_by"],
        "result":         str(meta["win_outcome"]),
        "player_of_match": str(meta["player_of_match"]),
        "stage":          str(meta["stage"]),
    }

    innings_data = {}
    for inn in [1, 2]:
        idf = md[md["innings"] == inn]
        if idf.empty:
            continue

        # Over-by-over
        overs = []
        for over_num, over_df in idf.groupby("over"):
            over_runs  = int(over_df["runs_total"].sum())
            over_wkts  = int(over_df["bowler_wicket"].sum())
            cum_runs   = int(idf[idf["over"] <= over_num]["runs_total"].sum())
            cum_wkts   = int(idf[idf["over"] <= over_num]["bowler_wicket"].sum())
            bowler     = over_df["bowler"].iloc[0]
            key_balls  = []

            for _, ball in over_df.iterrows():
                if ball["runs_batter"] >= 4 or ball["bowler_wicket"] == 1:
                    key_balls.append({
                        "ball":      f"{int(over_num)}.{int(ball['ball'])}",
                        "batter":    ball["batter"],
                        "bowler":    ball["bowler"],
                        "runs":      int(ball["runs_batter"]),
                        "wicket":    str(ball["wicket_kind"]) if ball["bowler_wicket"] == 1 else None,
                        "dismissed": str(ball["player_out"]) if ball["bowler_wicket"] == 1 else None,
                    })

            overs.append({
                "over":      int(over_num) + 1,
                "runs":      over_runs,
                "wickets":   over_wkts,
                "bowler":    bowler,
                "cumulative_score": f"{cum_runs}/{cum_wkts}",
                "key_balls": key_balls,
            })

        # Top performers
        top_bat = (
            idf.groupby("batter")["runs_batter"].sum()
            .sort_values(ascending=False).head(3)
        )
        top_bowl = (
            idf.groupby("bowler")["bowler_wicket"].sum()
            .sort_values(ascending=False).head(3)
        )

        # Wicket log
        wickets = idf[idf["bowler_wicket"] == 1][[
            "over", "batter", "bowler", "wicket_kind"
        ]].copy()

        innings_data[f"innings_{inn}"] = {
            "batting_team": idf["batting_team"].iloc[0],
            "total_runs":   int(idf["runs_total"].sum()),
            "total_wickets":int(idf["bowler_wicket"].sum()),
            "overs_played": int(idf["over"].max()) + 1,
            "top_batters":  {k: int(v) for k, v in top_bat.items()},
            "top_bowlers":  {k: int(v) for k, v in top_bowl.items()},
            "wicket_log":   [
                {
                    "over":    int(r["over"]) + 1,
                    "batter":  r["batter"],
                    "bowler":  r["bowler"],
                    "kind":    str(r["wicket_kind"]),
                }
                for _, r in wickets.iterrows()
            ],
            "over_by_over": overs,
        }

    return result


def _build_prompt(summary, mode):
    """Build the Claude prompt based on commentary mode."""
    meta = summary["meta"]
    inn1 = summary.get("innings_1", {})
    inn2 = summary.get("innings_2", {})

    match_context = f"""
MATCH: {meta['team1']} vs {meta['team2']}
VENUE: {meta['venue']} | DATE: {meta['date']} | SEASON: {meta['season']}
STAGE: {meta['stage']}
RESULT: {meta['winner']} won by {meta['result']}
PLAYER OF THE MATCH: {meta['player_of_match']}

INNINGS 1 — {inn1.get('batting_team','')}: {inn1.get('total_runs',0)}/{inn1.get('total_wickets',0)}
Top batters: {inn1.get('top_batters',{})}
Top bowlers: {inn1.get('top_bowlers',{})}
Wickets: {inn1.get('wicket_log',[])}

INNINGS 2 — {inn2.get('batting_team','')}: {inn2.get('total_runs',0)}/{inn2.get('total_wickets',0)}
Top batters: {inn2.get('top_batters',{})}
Top bowlers: {inn2.get('top_bowlers',{})}
Wickets: {inn2.get('wicket_log',[])}

OVER-BY-OVER (Innings 1):
{json.dumps(inn1.get('over_by_over',[])[:10], indent=2)}

OVER-BY-OVER (Innings 2):
{json.dumps(inn2.get('over_by_over',[])[:10], indent=2)}
"""

    if mode == "🎙️ Full Match Commentary":
        return f"""You are a legendary cricket TV commentator — think Richie Benaud, Harsha Bhogle, and Ian Botham combined. Generate vivid, exciting ball-by-ball match commentary for this IPL match.

{match_context}

Write commentary structured as:
1. **Pre-match buildup** (2-3 sentences setting the scene)
2. **Innings 1 — Over by over commentary** (cover key overs, boundaries, wickets with vivid language)
3. **Innings break analysis** (2-3 sentences)
4. **Innings 2 — Over by over commentary** (cover the chase, pressure moments, key wickets)
5. **Match verdict** (dramatic conclusion with Player of the Match spotlight)

Use cricket vocabulary: cover drives, yorkers, mistimed pull, caught at deep midwicket, etc.
Be dramatic. Be specific. Reference actual player names and scores from the data.
Make it feel like you are watching this live on television.
Target length: 600-800 words."""

    elif mode == "📻 Radio Commentary":
        return f"""You are a BBC radio cricket commentator — the listener cannot see the match. Paint vivid pictures with words only. Generate punchy, descriptive radio commentary for this IPL match.

{match_context}

Write in real-time radio style:
- Short, punchy sentences
- Describe field settings, body language, crowd reactions
- Build tension ball by ball for key moments
- Include crowd noise descriptions [ROAR FROM THE CROWD], [GASPS]
- Reference actual scores and player names throughout

Structure: Pre-match → Innings 1 highlights → Innings break → Innings 2 highlights → Result
Target length: 500-600 words."""

    elif mode == "📊 Analyst Breakdown":
        return f"""You are a data-driven cricket analyst on a post-match show. Give a sharp, tactical breakdown of this IPL match — like Anil Kumble or Sanjay Manjrekar doing analysis.

{match_context}

Structure your analysis as:
1. **Match summary** (2-3 sentences)
2. **Batting analysis** — where runs came from, powerplay vs middle vs death, key partnerships
3. **Bowling analysis** — who strangled the scoring, who got hit, economy comparison
4. **Turning point** — the single over or wicket that changed the match
5. **Player ratings** — rate the top 3 performers out of 10 with brief justification
6. **Tactical verdict** — what the winning team did right, what the losing team did wrong

Be specific with numbers. Reference actual overs and scores from the data.
Target length: 500-600 words."""

    elif mode == "🔥 Twitter Thread":
        return f"""You are a popular cricket Twitter account with 500K followers. Write a live Twitter thread covering this IPL match. Each tweet should be punchy, use cricket hashtags, and feel like real live tweeting.

{match_context}

Write 10-12 tweets as a thread. Format each as:
[Tweet 1/12] text here #IPL #cricket

Include:
- Opening hype tweet
- Powerplay reaction
- Key wicket reactions (use CAPS for shock moments)
- Boundary celebrations  
- Innings break take
- Chase tweets
- Match result tweet
- Player of match tweet

Use emojis naturally: 🏏 💥 🔥 😱 👏
Keep each tweet under 280 characters.
Reference actual player names and scores."""



def call_llm(prompt: str, provider_name: str, api_key: str) -> str:
    """
    Call whichever free provider the user picked.
    Uses only the `requests` library — no pip install needed.
    """
    cfg = PROVIDERS[provider_name]
    url = cfg["url"]
    fmt = cfg["fmt"]
    model = cfg["model"]

    try:
        if fmt == "openai":
            # Groq and OpenRouter both use OpenAI-compatible format
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1500,
                "temperature": 0.8,
            }
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            data = resp.json()

            if "error" in data:
                err = data["error"]
                msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                return f"❌ API Error: {msg}"

            return data["choices"][0]["message"]["content"]

        elif fmt == "gemini":
            # Google Gemini uses its own format
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            }
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 1500, "temperature": 0.8},
            }
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            data = resp.json()

            if "error" in data:
                return f"❌ API Error: {data['error'].get('message', 'Unknown error')}"

            candidates = data.get("candidates", [])
            if not candidates:
                return "❌ No response from Gemini. Check your API key."
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts)

    except requests.exceptions.Timeout:
        return "❌ Request timed out. Try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ════════════════════════════════════════════════════════════════
# CHART HELPERS
# ════════════════════════════════════════════════════════════════
def _worm_chart(data, match_id, team1, team2):
    """Cumulative runs worm chart for both innings."""
    md = data[data["match_id"] == match_id]
    inn1 = md[md["innings"] == 1].groupby("over")["runs_total"].sum().cumsum()
    inn2 = md[md["innings"] == 2].groupby("over")["runs_total"].sum().cumsum()

    fig, ax = plt.subplots(figsize=(10, 4))
    apply_dark_style(fig, ax,
                     title="Match worm — cumulative runs",
                     xlabel="Over", ylabel="Runs")

    t1_col = team_color(team1)
    t2_col = team_color(team2)

    ax.plot(inn1.index + 1, inn1.values,
            color=t1_col, linewidth=2.5, marker="o", markersize=3, label=f"{team1[:15]} (Inn 1)")
    ax.plot(inn2.index + 1, inn2.values,
            color=t2_col, linewidth=2.5, marker="s", markersize=3,
            linestyle="--", label=f"{team2[:15]} (Inn 2)")

    ax.fill_between(inn1.index + 1, inn1.values, alpha=0.08, color=t1_col)
    ax.fill_between(inn2.index + 1, inn2.values, alpha=0.08, color=t2_col)

    ax.legend(facecolor="#1a1f2a", labelcolor=TEXT_COLOR, fontsize=9)
    plt.tight_layout()
    return fig


def _over_runs_chart(data, match_id, innings, team_name):
    """Bar chart of runs per over for one innings."""
    md = data[(data["match_id"] == match_id) & (data["innings"] == innings)]
    over_runs = md.groupby("over")["runs_total"].sum()
    over_wkts = md.groupby("over")["bowler_wicket"].sum()

    t_col = team_color(team_name)
    colors = [ACCENT3 if over_wkts.get(ov, 0) > 0 else t_col
              for ov in over_runs.index]

    fig, ax = plt.subplots(figsize=(10, 3.5))
    apply_dark_style(fig, ax,
                     title=f"Innings {innings} — runs per over ({team_name[:20]})",
                     xlabel="Over", ylabel="Runs")

    bars = ax.bar(over_runs.index + 1, over_runs.values, color=colors, width=0.7)

    # Wicket markers
    for ov, wkt in over_wkts.items():
        if wkt > 0:
            ax.text(ov + 1, over_runs.get(ov, 0) + 0.3, "🔴" * wkt,
                    ha="center", fontsize=8)

    normal  = mpatches.Patch(color=t_col,   label="Normal over")
    wicket  = mpatches.Patch(color=ACCENT3, label="Wicket over")
    ax.legend(handles=[normal, wicket], facecolor="#1a1f2a",
              labelcolor=TEXT_COLOR, fontsize=8)
    plt.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════════
# MAIN VIEW
# ════════════════════════════════════════════════════════════════
def show_commentator_view(data):

    # ── page styles ──────────────────────────────────────────────
    st.markdown("""
    <style>
    .comm-hero {
        background: linear-gradient(135deg, rgba(0,0,0,0.6), rgba(255,107,107,0.15));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px; padding: 24px 26px; margin-bottom: 20px;
    }
    .comm-title { font-size: 28px; font-weight: 800; color: white; margin: 0 0 6px; }
    .comm-sub   { font-size: 14px; color: rgba(255,255,255,0.55); }

    .match-info-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 16px 18px; margin-bottom: 16px;
    }
    .score-block {
        background: rgba(0,0,0,0.35);
        border-radius: 10px; padding: 14px 18px;
        text-align: center;
    }
    .score-runs  { font-size: 32px; font-weight: 800; color: white; }
    .score-team  { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 4px; }
    .score-extra { font-size: 12px; color: rgba(255,255,255,0.35); }

    .commentary-output {
        background: rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px; padding: 22px 24px;
        font-size: 14px; line-height: 1.9;
        color: rgba(255,255,255,0.85);
        white-space: pre-wrap; word-wrap: break-word;
        margin-top: 16px;
    }
    .mode-badge {
        display: inline-block; padding: 4px 14px;
        border-radius: 99px; font-size: 12px; font-weight: 700;
        background: rgba(0,255,255,0.1); color: #00FFFF;
        border: 1px solid rgba(0,255,255,0.3);
        margin-bottom: 14px;
    }
    .stat-row {
        display: flex; justify-content: space-between;
        padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.06);
        font-size: 13px;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: rgba(255,255,255,0.5); }
    .stat-val   { color: white; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    # ── hero ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="comm-hero">
        <div class="comm-title">🎙️ AI Match Commentator</div>
        <div class="comm-sub">
            Powered by Claude AI · Select any IPL match · Get broadcast-quality commentary,
            tactical analysis, or a live Twitter thread — generated from real ball-by-ball data
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── match selector ───────────────────────────────────────────
    matches = get_match_list(data)

    st.markdown("<h3 style='color:white;margin:0 0 12px;'>🏏 Select a Match</h3>",
                unsafe_allow_html=True)

    col_search, col_season = st.columns([3, 1])
    with col_season:
        seasons = ["All seasons"] + sorted(data["season"].dropna().astype(str).unique().tolist(), reverse=True)
        chosen_season = st.selectbox("Filter by season", seasons)

    with col_search:
        if chosen_season != "All seasons":
            filtered = matches[matches["season"].astype(str) == chosen_season]
        else:
            filtered = matches

        if filtered.empty:
            st.warning("No matches for this season.")
            return

        selected_label = st.selectbox(
            "Choose match",
            filtered["label"].tolist(),
            index=0,
        )

    selected_row = filtered[filtered["label"] == selected_label].iloc[0]
    match_id     = int(selected_row["match_id"])
    team1        = selected_row["batting_team"]
    team2        = selected_row["bowling_team"]
    winner       = selected_row["match_won_by"]
    result       = selected_row["win_outcome"]
    pom          = selected_row["player_of_match"]
    venue        = selected_row["venue"]
    t1_col       = team_color(team1)
    t2_col       = team_color(team2)

    # ── match scorecard ──────────────────────────────────────────
    st.markdown("<h3 style='color:white;margin:20px 0 12px;'>📋 Match Scorecard</h3>",
                unsafe_allow_html=True)

    md = data[data["match_id"] == match_id]
    inn1_total = int(md[md["innings"] == 1]["runs_total"].sum())
    inn1_wkts  = int(md[md["innings"] == 1]["bowler_wicket"].sum())
    inn2_total = int(md[md["innings"] == 2]["runs_total"].sum())
    inn2_wkts  = int(md[md["innings"] == 2]["bowler_wicket"].sum())

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="score-block" style="border-left:4px solid {t1_col};">
            <div class="score-runs" style="color:{t1_col};">{inn1_total}/{inn1_wkts}</div>
            <div class="score-team">{team1[:22]}</div>
            <div class="score-extra">Innings 1</div>
        </div>""", unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
        <div style="text-align:center; padding:20px 0;">
            <div style="font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:6px;">RESULT</div>
            <div style="font-size:16px;font-weight:800;color:#FFE66D;">{winner[:18]}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;">won by {result}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-top:6px;">
                🏆 POM: {pom}
            </div>
        </div>""", unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
        <div class="score-block" style="border-left:4px solid {t2_col};">
            <div class="score-runs" style="color:{t2_col};">{inn2_total}/{inn2_wkts}</div>
            <div class="score-team">{team2[:22]}</div>
            <div class="score-extra">Innings 2</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── match info grid ──────────────────────────────────────────
    st.markdown(f"""
    <div class="match-info-card">
        <div class="stat-row">
            <span class="stat-label">📍 Venue</span>
            <span class="stat-val">{venue}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">📅 Date</span>
            <span class="stat-val">{selected_row['date']}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">🏆 Stage</span>
            <span class="stat-val">{selected_row['stage']}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">📊 Total balls in dataset</span>
            <span class="stat-val">{len(md):,} deliveries</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── worm chart ───────────────────────────────────────────────
    st.markdown("<h3 style='color:white;margin:16px 0 10px;'>📈 Match Worm</h3>",
                unsafe_allow_html=True)
    fig_worm = _worm_chart(data, match_id, team1, team2)
    st.pyplot(fig_worm)

    # ── over-by-over charts ───────────────────────────────────────
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_inn1 = _over_runs_chart(data, match_id, 1, team1)
        st.pyplot(fig_inn1)
    with col_c2:
        fig_inn2 = _over_runs_chart(data, match_id, 2, team2)
        st.pyplot(fig_inn2)

    st.markdown("---")

    # ── commentary mode selector ──────────────────────────────────
    st.markdown("<h3 style='color:white;margin:0 0 12px;'>🎙️ Generate AI Commentary</h3>",
                unsafe_allow_html=True)

    mode = st.radio(
        "Choose commentary style",
        ["🎙️ Full Match Commentary", "📻 Radio Commentary",
         "📊 Analyst Breakdown", "🔥 Twitter Thread"],
        horizontal=True,
    )

    mode_desc = {
        "🎙️ Full Match Commentary": "Richie Benaud-style TV commentary — vivid, dramatic, ball-by-ball",
        "📻 Radio Commentary":      "BBC radio style — paint pictures with words, no visuals",
        "📊 Analyst Breakdown":     "Post-match tactical analysis with player ratings",
        "🔥 Twitter Thread":        "10-12 live tweets covering the full match",
    }
    st.markdown(
        f"<p style='color:rgba(255,255,255,0.45);font-size:13px;margin-bottom:20px;'>"
        f"{mode_desc[mode]}</p>",
        unsafe_allow_html=True,
    )

    # ── FREE API provider picker ──────────────────────────────────
    st.markdown(
        "<h3 style='color:white;margin:4px 0 10px;'>🔑 Choose Free AI Provider</h3>",
        unsafe_allow_html=True,
    )

    provider_name = st.selectbox(
        "AI Provider — all 100% free, no credit card",
        list(PROVIDERS.keys()),
        index=0,
    )
    cfg = PROVIDERS[provider_name]

    st.markdown(
        f"<p style='color:rgba(255,255,255,0.4);font-size:12px;margin:4px 0 10px;'>"
        f"Get your free key → <b>{cfg['signup']}</b></p>",
        unsafe_allow_html=True,
    )

    api_key = st.text_input(
        "Your API key HERE",
        type="password",
        placeholder="Your key stays local — only sent to the provider you chose",
    )

    generate_btn = st.button("⚡ Generate Commentary", use_container_width=True)

    if generate_btn:
        if not api_key or len(api_key) < 8:
            st.warning("⚠️ Paste your API key above first.")
            return

        with st.spinner("🎙️ AI is watching the match..."):
            summary = _build_match_summary(data, match_id)
            if summary is None:
                st.error("Could not load match data.")
                return

            prompt     = _build_prompt(summary, mode)
            commentary = call_llm(prompt, provider_name, api_key)

        if commentary.startswith("❌"):
            st.error(commentary)
            st.markdown(
                f"<p style='font-size:13px;color:rgba(255,255,255,0.5);'>"
                f"Check your key is correct and get a new one at <b>{cfg['signup']}</b></p>",
                unsafe_allow_html=True,
            )
            return

        st.markdown(f'<div class="mode-badge">{mode}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="commentary-output">{commentary}</div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "📋 Copy commentary",
            value=commentary,
            height=200,
            help="Select all and copy",
        )

    # ── resume talking point ──────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style='background:rgba(0,255,255,0.05);border:1px solid rgba(0,255,255,0.2);
                border-radius:12px;padding:16px 18px;'>
        <p style='color:#00FFFF;font-size:13px;font-weight:700;margin:0 0 6px;'>
            💼 Resume talking point
        </p>
        <p style='color:rgba(255,255,255,0.7);font-size:13px;line-height:1.7;margin:0;'>
            "Integrated free LLM APIs (Groq Llama 3.3 70B / Google Gemini) into a deployed
            Streamlit cricket analytics app — generates broadcast-quality match commentary,
            tactical analysis and social content from real IPL ball-by-ball data using
            prompt engineering and structured data serialisation."
        </p>
    </div>
    """, unsafe_allow_html=True)
