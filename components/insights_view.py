import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show_insights(data):

    st.markdown("<h2>📊 Advanced Insights</h2>", unsafe_allow_html=True)

    # TOP RUN SCORERS
    top = data.groupby('batter')['runs_batter'].sum().sort_values(ascending=False).head(5)

    st.markdown("<h3>🏏 Top Run Scorers</h3>", unsafe_allow_html=True)

    for player, runs in top.items():
        st.markdown(f"<div class='card'>{player} — {runs} runs</div>", unsafe_allow_html=True)

    # CONSISTENT PLAYERS
    df = data.groupby('batter').agg({
        'runs_batter': 'sum',
        'balls_faced': 'sum'
    })

    df = df[df['balls_faced'] > 500]

    if not df.empty:
        df['avg'] = df['runs_batter'] / df['balls_faced']

        consistent = df.sort_values(by='avg', ascending=False).head(5)

        st.markdown("<h3>🎯 Most Consistent</h3>", unsafe_allow_html=True)

        for player, row in consistent.iterrows():
            st.markdown(f"<div class='card'>{player} — Avg: {round(row['avg'],2)}</div>", unsafe_allow_html=True)

        # AGGRESSIVE PLAYERS
        df['sr'] = df['runs_batter'] / df['balls_faced'] * 100
        aggressive = df.sort_values(by='sr', ascending=False).head(5)

        st.markdown("<h3>🚀 Most Aggressive</h3>", unsafe_allow_html=True)

        for player, row in aggressive.iterrows():
            st.markdown(f"<div class='card'>{player} — SR: {round(row['sr'],2)}</div>", unsafe_allow_html=True)

    # HOW IPL SCORING HAS EVOLVED — fixed season sort
    st.markdown("<h3>📅 How IPL Scoring Has Evolved</h3>", unsafe_allow_html=True)

    season_runs = (
        data.groupby("season")["runs_total"].mean()
        .reset_index()
    )
    # ← FIX: convert to string before sorting (mixed int/str types)
    season_runs["season"] = season_runs["season"].astype(str)
    season_runs["season"] = season_runs["season"].astype(str)
    seasons_sorted = season_runs.sort_values("season")
    seasons_sorted = season_runs.sort_values("season")
    

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_facecolor("#0e1117")
    fig.patch.set_facecolor("#0e1117")
    ax.plot(
        range(len(seasons_sorted)),
        seasons_sorted["runs_total"],
        color="#00e5ff", linewidth=2.5, marker="o", markersize=5,
    )
    ax.fill_between(range(len(seasons_sorted)), seasons_sorted["runs_total"],
                    alpha=0.1, color="#00e5ff")
    ax.set_xticks(range(len(seasons_sorted)))
    ax.set_xticklabels(seasons_sorted["season"].tolist(),
                       rotation=45, ha="right", color="#aaa", fontsize=8)
    ax.set_ylabel("Avg Runs/Ball", color="#aaa", fontsize=9)
    ax.tick_params(colors="#aaa")
    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
    ax.grid(True, color="#1e2530", linewidth=0.5, linestyle="--", alpha=0.6)
    ax.set_title("Average Runs per Ball by Season", color="white", fontsize=11)
    plt.tight_layout()
    st.pyplot(fig)
