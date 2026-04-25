import streamlit as st
import pandas as pd
import json
import requests
import os
from groq import Groq
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from utils.chart_style import (
    apply_dark_style, dark_line_chart,
    DARK_BG, ACCENT, ACCENT2, ACCENT3, TEXT_COLOR,
    team_color
)

# ==========================================================
# GROQ API CONFIG
# ==========================================================
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GROQ_MODEL = "llama3-70b-8192"

client = Groq(api_key=GROQ_API_KEY)

# ==========================================================
# DATA HELPERS
# ==========================================================
@st.cache_data
def get_match_list(data):
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

    matches["label"] = (
        matches["season"].astype(str) + " | "
        + matches["batting_team"].str[:12] + " vs "
        + matches["bowling_team"].str[:12] + " — "
        + matches["venue"].str.split(",").str[0].str[:20]
    )

    return matches


def _build_match_summary(data, match_id):
    md = data[data["match_id"] == match_id].sort_values(
        ["innings", "over", "ball"]
    )

    if md.empty:
        return None

    meta = md.iloc[0]

    result = {
        "meta": {
            "team1": meta["batting_team"],
            "team2": meta["bowling_team"],
            "venue": meta["venue"],
            "date": str(meta["date"]),
            "season": str(meta["season"]),
            "winner": meta["match_won_by"],
            "result": str(meta["win_outcome"]),
            "player_of_match": str(meta["player_of_match"]),
            "stage": str(meta["stage"]),
        }
    }

    innings_data = {}

    for inn in [1, 2]:
        idf = md[md["innings"] == inn]

        if idf.empty:
            continue

        overs = []

        for over_num, over_df in idf.groupby("over"):

            over_runs = int(over_df["runs_total"].sum())
            over_wkts = int(over_df["bowler_wicket"].sum())

            cum_runs = int(
                idf[idf["over"] <= over_num]["runs_total"].sum()
            )

            cum_wkts = int(
                idf[idf["over"] <= over_num]["bowler_wicket"].sum()
            )

            bowler = over_df["bowler"].iloc[0]

            key_balls = []

            for _, ball in over_df.iterrows():

                if ball["runs_batter"] >= 4 or ball["bowler_wicket"] == 1:
                    key_balls.append({
                        "ball": f"{int(over_num)}.{int(ball['ball'])}",
                        "batter": ball["batter"],
                        "bowler": ball["bowler"],
                        "runs": int(ball["runs_batter"]),
                        "wicket": str(ball["wicket_kind"])
                        if ball["bowler_wicket"] == 1 else None,
                        "dismissed": str(ball["player_out"])
                        if ball["bowler_wicket"] == 1 else None,
                    })

            overs.append({
                "over": int(over_num) + 1,
                "runs": over_runs,
                "wickets": over_wkts,
                "bowler": bowler,
                "cumulative_score": f"{cum_runs}/{cum_wkts}",
                "key_balls": key_balls,
            })

        top_bat = (
            idf.groupby("batter")["runs_batter"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
        )

        top_bowl = (
            idf.groupby("bowler")["bowler_wicket"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
        )

        wickets = idf[idf["bowler_wicket"] == 1][[
            "over", "batter", "bowler", "wicket_kind"
        ]].copy()

        innings_data[f"innings_{inn}"] = {
            "batting_team": idf["batting_team"].iloc[0],
            "total_runs": int(idf["runs_total"].sum()),
            "total_wickets": int(idf["bowler_wicket"].sum()),
            "overs_played": int(idf["over"].max()) + 1,
            "top_batters": {k: int(v) for k, v in top_bat.items()},
            "top_bowlers": {k: int(v) for k, v in top_bowl.items()},
            "wicket_log": [
                {
                    "over": int(r["over"]) + 1,
                    "batter": r["batter"],
                    "bowler": r["bowler"],
                    "kind": str(r["wicket_kind"]),
                }
                for _, r in wickets.iterrows()
            ],
            "over_by_over": overs,
        }

    result.update(innings_data)
    return result


# ==========================================================
# PROMPT BUILDER
# ==========================================================
def _build_prompt(summary, mode):
    meta = summary["meta"]
    inn1 = summary.get("innings_1", {})
    inn2 = summary.get("innings_2", {})

    match_context = f"""
MATCH: {meta['team1']} vs {meta['team2']}
VENUE: {meta['venue']}
DATE: {meta['date']}
SEASON: {meta['season']}
RESULT: {meta['winner']} won by {meta['result']}
PLAYER OF MATCH: {meta['player_of_match']}

INNINGS 1:
{json.dumps(inn1, indent=2)}

INNINGS 2:
{json.dumps(inn2, indent=2)}
"""

    if mode == "🎙️ Full Match Commentary":
        return f"""
You are a world-class IPL commentator.

Generate dramatic TV style commentary.

{match_context}

Make it exciting.
Use player names.
Use cricket language.
600 words.
"""

    elif mode == "📻 Radio Commentary":
        return f"""
You are radio commentator.

Generate vivid commentary for blind listeners.

{match_context}

500 words.
"""

    elif mode == "📊 Analyst Breakdown":
        return f"""
You are cricket analyst.

Give tactical breakdown.

{match_context}

Include turning point, player ratings.
"""

    else:
        return f"""
You are cricket Twitter page.

Create 10 tweets thread.

{match_context}
"""


# ==========================================================
# GROQ CALL
# ==========================================================
def call_groq(prompt):
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Groq Error: {str(e)}"


# ==========================================================
# CHARTS
# ==========================================================
def _worm_chart(data, match_id, team1, team2):

    md = data[data["match_id"] == match_id]

    inn1 = md[md["innings"] == 1].groupby("over")["runs_total"].sum().cumsum()
    inn2 = md[md["innings"] == 2].groupby("over")["runs_total"].sum().cumsum()

    fig, ax = plt.subplots(figsize=(10, 4))

    apply_dark_style(
        fig, ax,
        title="Match Worm",
        xlabel="Over",
        ylabel="Runs"
    )

    ax.plot(
        inn1.index + 1,
        inn1.values,
        linewidth=2.5,
        marker="o",
        label=team1
    )

    ax.plot(
        inn2.index + 1,
        inn2.values,
        linewidth=2.5,
        linestyle="--",
        marker="s",
        label=team2
    )

    ax.legend()
    plt.tight_layout()
    return fig


# ==========================================================
# MAIN VIEW
# ==========================================================
def show_commentator_view(data):

    st.title("🎙️ AI Match Commentator (Groq Powered)")

    matches = get_match_list(data)

    selected_label = st.selectbox(
        "Select Match",
        matches["label"].tolist()
    )

    row = matches[matches["label"] == selected_label].iloc[0]

    match_id = int(row["match_id"])
    team1 = row["batting_team"]
    team2 = row["bowling_team"]

    st.subheader(f"{team1} vs {team2}")

    md = data[data["match_id"] == match_id]

    inn1_total = int(md[md["innings"] == 1]["runs_total"].sum())
    inn1_wkts = int(md[md["innings"] == 1]["bowler_wicket"].sum())

    inn2_total = int(md[md["innings"] == 2]["runs_total"].sum())
    inn2_wkts = int(md[md["innings"] == 2]["bowler_wicket"].sum())

    c1, c2 = st.columns(2)

    with c1:
        st.metric(team1, f"{inn1_total}/{inn1_wkts}")

    with c2:
        st.metric(team2, f"{inn2_total}/{inn2_wkts}")

    fig = _worm_chart(data, match_id, team1, team2)
    st.pyplot(fig)

    mode = st.radio(
        "Choose Mode",
        [
            "🎙️ Full Match Commentary",
            "📻 Radio Commentary",
            "📊 Analyst Breakdown",
            "🔥 Twitter Thread"
        ],
        horizontal=True
    )

    if st.button("⚡ Generate Commentary"):

        with st.spinner("Generating using Groq..."):

            summary = _build_match_summary(data, match_id)
            prompt = _build_prompt(summary, mode)

            commentary = call_groq(prompt)

        st.success("Generated!")

        st.text_area(
            "Output",
            commentary,
            height=500
        )