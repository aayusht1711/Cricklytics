import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


KNOCKOUT_STAGES = [
    "Final",
    "Semi Final",
    "Qualifier 1",
    "Qualifier 2",
    "Eliminator",
    "Elimination Final",
    "3rd Place Play-Off",
]


@st.cache_data
def _clutch_batter_stats(data):
    ko = data[data["stage"].isin(KNOCKOUT_STAGES)]
    league = data[data["stage"] == "Unknown"]

    def batter_agg(df):
        return (
            df.groupby("batter")
            .agg(runs=("runs_batter", "sum"), balls=("balls_faced", "sum"))
            .reset_index()
        )

    ko_bat = batter_agg(ko).rename(columns={"runs": "ko_runs", "balls": "ko_balls"})
    lg_bat = batter_agg(league).rename(columns={"runs": "lg_runs", "balls": "lg_balls"})

    merged = ko_bat.merge(lg_bat, on="batter")
    merged = merged[(merged["ko_balls"] >= 50) & (merged["lg_balls"] >= 200)]

    merged["ko_sr"] = (merged["ko_runs"] / merged["ko_balls"] * 100).round(2)
    merged["lg_sr"] = (merged["lg_runs"] / merged["lg_balls"] * 100).round(2)
    merged["sr_lift"] = (merged["ko_sr"] - merged["lg_sr"]).round(2)

    return merged


@st.cache_data
def _clutch_bowler_stats(data):
    ko = data[data["stage"].isin(KNOCKOUT_STAGES)]
    league = data[data["stage"] == "Unknown"]

    def bowler_agg(df):
        return (
            df.groupby("bowler")
            .agg(
                runs=("runs_bowler", "sum"),
                balls=("valid_ball", "sum"),
                wickets=("bowler_wicket", "sum"),
            )
            .reset_index()
        )

    ko_bowl = bowler_agg(ko).rename(
        columns={"runs": "ko_runs", "balls": "ko_balls", "wickets": "ko_wkts"}
    )
    lg_bowl = bowler_agg(league).rename(
        columns={"runs": "lg_runs", "balls": "lg_balls", "wickets": "lg_wkts"}
    )

    merged = ko_bowl.merge(lg_bowl, on="bowler")
    merged = merged[(merged["ko_balls"] >= 30) & (merged["lg_balls"] >= 120)]

    merged["ko_econ"] = (merged["ko_runs"] / merged["ko_balls"] * 6).round(2)
    merged["lg_econ"] = (merged["lg_runs"] / merged["lg_balls"] * 6).round(2)
    merged["econ_drop"] = (merged["lg_econ"] - merged["ko_econ"]).round(2)

    return merged


def show_knockout_view(data):
    st.markdown("<h2>🏆 Knockout Filter — Clutch Performers</h2>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class='card'>
        <p style='color:rgba(255,255,255,0.7); font-size:14px;'>
        This view compares <b>Knockout performance</b> (Finals, Semi Finals, Qualifiers, Eliminators)
        vs <b>League stage</b> to identify players who truly perform under pressure.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(
        ["🏏 Clutch Batters", "🎯 Clutch Bowlers", "🔍 Player Deep Dive"]
    )

    bat_df = _clutch_batter_stats(data)
    bowl_df = _clutch_bowler_stats(data)

    # -------- TAB 1: Clutch Batters --------
    with tab1:
        st.markdown("<h3>🔥 Most Runs in Knockouts</h3>", unsafe_allow_html=True)
        top_ko = bat_df.sort_values("ko_runs", ascending=False).head(10)
        for i, r in enumerate(top_ko.itertuples(), 1):
            sr_tag = (
                f"<span style='color:#4ECDC4;'>▲ SR +{r.sr_lift}</span>"
                if r.sr_lift > 0
                else f"<span style='color:#FF6B6B;'>▼ SR {r.sr_lift}</span>"
            )
            st.markdown(
                f"<div class='card'>#{i} &nbsp; 🏏 <b>{r.batter}</b>"
                f" — KO: {r.ko_runs} runs @ SR {r.ko_sr}"
                f" &nbsp;|&nbsp; League SR: {r.lg_sr} &nbsp; {sr_tag}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<h3>⚡ Biggest SR Boost in Knockouts</h3>", unsafe_allow_html=True)
        st.caption("Players whose SR increases the most in knockouts vs league games")
        big_lift = bat_df.sort_values("sr_lift", ascending=False).head(8)

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")

        x = range(len(big_lift))
        w = 0.35
        b1 = ax.bar([i - w / 2 for i in x], big_lift["ko_sr"], w, label="Knockout SR", color="#FFE66D")
        b2 = ax.bar([i + w / 2 for i in x], big_lift["lg_sr"], w, label="League SR", color="#4ECDC4")

        ax.set_xticks(list(x))
        ax.set_xticklabels(big_lift["batter"], rotation=30, ha="right", color="white", fontsize=9)
        ax.set_ylabel("Strike Rate", color="white")
        ax.tick_params(colors="white")
        ax.spines[:].set_color("#444")
        ax.legend(facecolor="#0e1117", labelcolor="white")
        ax.set_title("Knockout SR vs League SR", color="white")
        plt.tight_layout()
        st.pyplot(fig)

    # -------- TAB 2: Clutch Bowlers --------
    with tab2:
        st.markdown("<h3>🎯 Most Wickets in Knockouts</h3>", unsafe_allow_html=True)
        top_bowl_ko = bowl_df.sort_values("ko_wkts", ascending=False).head(10)
        for i, r in enumerate(top_bowl_ko.itertuples(), 1):
            econ_tag = (
                f"<span style='color:#4ECDC4;'>▲ Econ improved +{r.econ_drop}</span>"
                if r.econ_drop > 0
                else f"<span style='color:#FF6B6B;'>▼ Econ worse {r.econ_drop}</span>"
            )
            st.markdown(
                f"<div class='card'>#{i} &nbsp; ⚡ <b>{r.bowler}</b>"
                f" — KO: {r.ko_wkts} wkts @ Econ {r.ko_econ}"
                f" &nbsp;|&nbsp; League Econ: {r.lg_econ} &nbsp; {econ_tag}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<h3>💨 Best Economy Improvement in Knockouts</h3>", unsafe_allow_html=True
        )
        st.caption("Bowlers whose economy rate drops (improves) the most in knockouts")
        best_econ = bowl_df[bowl_df["ko_wkts"] >= 3].sort_values(
            "econ_drop", ascending=False
        ).head(8)

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        fig2.patch.set_facecolor("#0e1117")
        ax2.set_facecolor("#0e1117")

        x2 = range(len(best_econ))
        ax2.bar([i - w / 2 for i in x2], best_econ["ko_econ"], w, label="Knockout Econ", color="#FF6B6B")
        ax2.bar([i + w / 2 for i in x2], best_econ["lg_econ"], w, label="League Econ", color="#4ECDC4")

        ax2.set_xticks(list(x2))
        ax2.set_xticklabels(best_econ["bowler"], rotation=30, ha="right", color="white", fontsize=9)
        ax2.set_ylabel("Economy Rate", color="white")
        ax2.tick_params(colors="white")
        ax2.spines[:].set_color("#444")
        ax2.legend(facecolor="#0e1117", labelcolor="white")
        ax2.set_title("Knockout Economy vs League Economy", color="white")
        plt.tight_layout()
        st.pyplot(fig2)

    # -------- TAB 3: Individual Deep Dive --------
    with tab3:
        st.markdown("<h3>🔍 Individual Knockout Profile</h3>", unsafe_allow_html=True)

        role = st.radio("Role", ["Batter", "Bowler"], horizontal=True)

        if role == "Batter":
            player = st.selectbox(
                "Select Batter",
                sorted(bat_df["batter"].unique()),
            )
            row = bat_df[bat_df["batter"] == player]
            if row.empty:
                st.warning("Not enough knockout data (min 50 balls in knockouts).")
            else:
                r = row.iloc[0]
                delta_color = "#4ECDC4" if r["sr_lift"] >= 0 else "#FF6B6B"
                arrow = "▲" if r["sr_lift"] >= 0 else "▼"
                st.markdown(
                    f"""
                <div class='card'>
                    <h3 style='color:#FFE66D;'>🏏 {player} — Knockout vs League</h3>
                    <table style='width:100%; color:white; font-size:15px; margin-top:10px;'>
                        <tr><th></th><th>🏆 Knockout</th><th>📋 League</th><th>Delta</th></tr>
                        <tr>
                            <td>Runs</td><td>{r['ko_runs']}</td><td>{r['lg_runs']}</td><td>—</td>
                        </tr>
                        <tr>
                            <td>Balls</td><td>{r['ko_balls']}</td><td>{r['lg_balls']}</td><td>—</td>
                        </tr>
                        <tr>
                            <td>Strike Rate</td><td>{r['ko_sr']}</td><td>{r['lg_sr']}</td>
                            <td style='color:{delta_color};'>{arrow} {abs(r['sr_lift'])}</td>
                        </tr>
                    </table>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Match-by-match knockout scores
                ko_data = data[
                    (data["stage"].isin(KNOCKOUT_STAGES)) & (data["batter"] == player)
                ]
                match_scores = (
                    ko_data.groupby(["match_id", "stage"])["runs_batter"]
                    .sum()
                    .reset_index()
                    .sort_values("runs_batter", ascending=False)
                )

                if not match_scores.empty:
                    st.markdown("<h4>🏆 Knockout Scores (per match)</h4>", unsafe_allow_html=True)
                    fig3, ax3 = plt.subplots(figsize=(10, 4))
                    fig3.patch.set_facecolor("#0e1117")
                    ax3.set_facecolor("#0e1117")
                    bar_colors = [
                        "#FFE66D" if s == "Final" else "#FF6B6B" if "Semi" in s else "#4ECDC4"
                        for s in match_scores["stage"]
                    ]
                    ax3.bar(
                        range(len(match_scores)),
                        match_scores["runs_batter"],
                        color=bar_colors,
                    )
                    ax3.set_xticks(range(len(match_scores)))
                    ax3.set_xticklabels(match_scores["stage"], rotation=30, ha="right", color="white", fontsize=8)
                    ax3.set_ylabel("Runs", color="white")
                    ax3.tick_params(colors="white")
                    ax3.spines[:].set_color("#444")

                    final_p = mpatches.Patch(color="#FFE66D", label="Final")
                    semi_p = mpatches.Patch(color="#FF6B6B", label="Semi Final")
                    other_p = mpatches.Patch(color="#4ECDC4", label="Qualifier/Eliminator")
                    ax3.legend(handles=[final_p, semi_p, other_p], facecolor="#0e1117", labelcolor="white")
                    plt.tight_layout()
                    st.pyplot(fig3)

        else:  # Bowler
            player = st.selectbox(
                "Select Bowler",
                sorted(bowl_df["bowler"].unique()),
            )
            row = bowl_df[bowl_df["bowler"] == player]
            if row.empty:
                st.warning("Not enough knockout data (min 30 balls in knockouts).")
            else:
                r = row.iloc[0]
                delta_color = "#4ECDC4" if r["econ_drop"] >= 0 else "#FF6B6B"
                arrow = "▲" if r["econ_drop"] >= 0 else "▼"
                st.markdown(
                    f"""
                <div class='card'>
                    <h3 style='color:#FF6B6B;'>⚡ {player} — Knockout vs League</h3>
                    <table style='width:100%; color:white; font-size:15px; margin-top:10px;'>
                        <tr><th></th><th>🏆 Knockout</th><th>📋 League</th><th>Delta</th></tr>
                        <tr>
                            <td>Wickets</td><td>{r['ko_wkts']}</td><td>{r['lg_wkts']}</td><td>—</td>
                        </tr>
                        <tr>
                            <td>Economy</td><td>{r['ko_econ']}</td><td>{r['lg_econ']}</td>
                            <td style='color:{delta_color};'>{arrow} {abs(r['econ_drop'])}</td>
                        </tr>
                    </table>
                </div>
                """,
                    unsafe_allow_html=True,
                )
