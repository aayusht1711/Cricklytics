import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


@st.cache_data
def _bowler_stats(data):
    df = data.copy()

    # Phase labels
    df["phase"] = pd.cut(
        df["over"],
        bins=[-1, 5, 14, 19],
        labels=["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"],
    )

    # Overall stats
    overall = (
        df.groupby("bowler")
        .agg(
            runs=("runs_total", "sum"),
            balls=("valid_ball", "sum"),
            wickets=("bowler_wicket", "sum"),
        )
        .reset_index()
    )
    overall = overall[overall["balls"] >= 120]
    overall["economy"] = (overall["runs"] / overall["balls"] * 6).round(2)
    overall["bowling_sr"] = (
        overall["balls"] / overall["wickets"].replace(0, float("nan"))
    ).round(2)
    overall["avg"] = (
        overall["runs"] / overall["wickets"].replace(0, float("nan"))
    ).round(2)

    # Phase-wise
    phase_stats = (
        df.groupby(["bowler", "phase"])
        .agg(runs=("runs_total", "sum"), balls=("valid_ball", "sum"))
        .reset_index()
    )
    phase_stats["economy"] = (phase_stats["runs"] / phase_stats["balls"] * 6).round(2)

    wickets_df = df[df["wicket_kind"].notna() & (df["bowler_wicket"] == 1)]
    wicket_types = (
        wickets_df.groupby(["bowler", "wicket_kind"])
        .size()
        .reset_index(name="count")
    )

    return overall, phase_stats, wicket_types


def show_bowler_view(data):
    st.markdown("<h2>🎯 Bowler Analytics</h2>", unsafe_allow_html=True)

    overall, phase_stats, wicket_types = _bowler_stats(data)

    bowler = st.selectbox(
        "Select Bowler", sorted(overall["bowler"].unique())
    )

    row = overall[overall["bowler"] == bowler]
    if row.empty:
        st.warning("Not enough data for this bowler (min 120 valid balls).")
        return
    row = row.iloc[0]

    # --- Main stats card ---
    st.markdown(
        f"""
    <div class='card'>
        <h3 style='color:#FF6B6B;'>⚡ {bowler}</h3>
        <table style='width:100%; color:white; font-size:15px; margin-top:10px;'>
            <tr>
                <td>🎯 Wickets</td><td><b>{int(row['wickets'])}</b></td>
                <td>💨 Economy</td><td><b>{row['economy']}</b></td>
            </tr>
            <tr>
                <td>📊 Bowling SR</td><td><b>{row['bowling_sr'] if pd.notna(row['bowling_sr']) else '—'}</b></td>
                <td>📈 Average</td><td><b>{row['avg'] if pd.notna(row['avg']) else '—'}</b></td>
            </tr>
            <tr>
                <td>⚾ Balls Bowled</td><td><b>{int(row['balls'])}</b></td>
                <td>💣 Runs Conceded</td><td><b>{int(row['runs'])}</b></td>
            </tr>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    # --- Wicket type pie chart ---
    with col1:
        st.markdown("<h3>🧩 Dismissal Types</h3>", unsafe_allow_html=True)
        wkt_row = wicket_types[wicket_types["bowler"] == bowler]
        if not wkt_row.empty:
            fig, ax = plt.subplots(figsize=(5, 4))
            fig.patch.set_facecolor("#0e1117")
            ax.set_facecolor("#0e1117")
            colors = ["#FF6B6B","#4ECDC4","#FFE66D","#A8E6CF","#FF8B94","#C7CEEA"]
            wedges, texts, autotexts = ax.pie(
                wkt_row["count"],
                labels=wkt_row["wicket_kind"],
                autopct="%1.0f%%",
                colors=colors[: len(wkt_row)],
                textprops={"color": "white", "fontsize": 8},
            )
            for at in autotexts:
                at.set_color("white")
            ax.set_title(f"{bowler} — How They Take Wickets", color="white", fontsize=10)
            st.pyplot(fig)
        else:
            st.info("No dismissal data available.")

    
    with col2:
        st.markdown("<h3>📊 Economy by Phase</h3>", unsafe_allow_html=True)
        phase_row = phase_stats[phase_stats["bowler"] == bowler]
        if not phase_row.empty:
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            fig2.patch.set_facecolor("#0e1117")
            ax2.set_facecolor("#0e1117")
            phase_colors = ["#4ECDC4", "#FFE66D", "#FF6B6B"]
            bars = ax2.bar(
                phase_row["phase"].astype(str),
                phase_row["economy"],
                color=phase_colors[: len(phase_row)],
            )
            ax2.set_ylabel("Economy Rate", color="white")
            ax2.tick_params(colors="white")
            ax2.spines[:].set_color("#444")
            for bar in bars:
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.1,
                    f"{bar.get_height():.2f}",
                    ha="center",
                    color="white",
                    fontsize=9,
                )
            ax2.set_title("Economy by Over Phase", color="white", fontsize=10)
            plt.xticks(rotation=10, ha="right")
            st.pyplot(fig2)
        else:
            st.info("No phase data available.")

    st.markdown("---")

    # --- Global Leaderboards ---
    st.markdown("<h3>🏆 Bowling Leaderboards</h3>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Most Wickets", "Best Economy", "Best Bowling SR"])

    with tab1:
        top_wkts = overall.sort_values("wickets", ascending=False).head(10)
        for i, r in enumerate(top_wkts.itertuples(), 1):
            highlight = "color:#00FFFF;" if r.bowler == bowler else ""
            st.markdown(
                f"<div class='card' style='{highlight}'>#{i} &nbsp; ⚡ <b>{r.bowler}</b>"
                f" — {int(r.wickets)} wkts &nbsp;|&nbsp; Econ: {r.economy}</div>",
                unsafe_allow_html=True,
            )

    with tab2:
        top_econ = overall[overall["balls"] >= 300].sort_values("economy").head(10)
        for i, r in enumerate(top_econ.itertuples(), 1):
            highlight = "color:#00FFFF;" if r.bowler == bowler else ""
            st.markdown(
                f"<div class='card' style='{highlight}'>#{i} &nbsp; 💨 <b>{r.bowler}</b>"
                f" — Econ: {r.economy} &nbsp;|&nbsp; {int(r.wickets)} wkts</div>",
                unsafe_allow_html=True,
            )

    with tab3:
        top_sr = overall[overall["wickets"] >= 20].sort_values("bowling_sr").head(10)
        for i, r in enumerate(top_sr.itertuples(), 1):
            highlight = "color:#00FFFF;" if r.bowler == bowler else ""
            st.markdown(
                f"<div class='card' style='{highlight}'>#{i} &nbsp; 🎯 <b>{r.bowler}</b>"
                f" — SR: {r.bowling_sr} &nbsp;|&nbsp; {int(r.wickets)} wkts</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # --- Death Overs Specialists ---
    st.markdown("<h3>💀 Death Over Specialists (Overs 16–19)</h3>", unsafe_allow_html=True)

    death = data[data["over"] >= 15].groupby("bowler").agg(
        runs=("runs_total", "sum"),
        balls=("valid_ball", "sum"),
        wickets=("bowler_wicket", "sum"),
    ).reset_index()
    death = death[death["balls"] >= 60]
    death["economy"] = (death["runs"] / death["balls"] * 6).round(2)
    death_top = death.sort_values("economy").head(5)

    for i, r in enumerate(death_top.itertuples(), 1):
        st.markdown(
            f"<div class='card'>#{i} &nbsp; 💀 <b>{r.bowler}</b>"
            f" — Death Econ: {r.economy} &nbsp;|&nbsp; {int(r.wickets)} wkts</div>",
            unsafe_allow_html=True,
        )
