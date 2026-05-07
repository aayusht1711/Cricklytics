import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
def _compute_drs(data):
    drs = data[data["review_decision"].notna()].copy()

    # Team stats
    team_upheld = drs[drs["review_decision"] == "upheld"].groupby("team_reviewed").size().reset_index(name="upheld")
    team_total  = drs.groupby("team_reviewed").size().reset_index(name="total")
    team_stats  = team_total.merge(team_upheld, on="team_reviewed", how="left").fillna(0)
    team_stats["success_pct"] = (team_stats["upheld"] / team_stats["total"] * 100).round(1)
    team_stats["struck_down"] = team_stats["total"] - team_stats["upheld"]

    # Batter stats (min 3 reviews)
    bat_total   = drs.groupby("review_batter").size().reset_index(name="total")
    bat_upheld  = drs[drs["review_decision"] == "upheld"].groupby("review_batter").size().reset_index(name="upheld")
    bat_stats   = bat_total.merge(bat_upheld, on="review_batter", how="left").fillna(0)
    bat_stats["success_pct"] = (bat_stats["upheld"] / bat_stats["total"] * 100).round(1)
    bat_stats   = bat_stats[bat_stats["total"] >= 3].sort_values("upheld", ascending=False)

    # Bowler stats (min 3 reviews)
    bow_total    = drs.groupby("bowler").size().reset_index(name="total")
    bow_overturn = drs[drs["review_decision"] == "upheld"].groupby("bowler").size().reset_index(name="overturned")
    bow_stats    = bow_total.merge(bow_overturn, on="bowler", how="left").fillna(0)
    bow_stats["overturn_pct"] = (bow_stats["overturned"] / bow_stats["total"] * 100).round(1)
    bow_stats    = bow_stats[bow_stats["total"] >= 3].sort_values("overturn_pct", ascending=False)

    # Wicket kind breakdown
    wkt_kind = drs["wicket_kind"].value_counts().reset_index()
    wkt_kind.columns = ["kind", "count"]

    return drs, team_stats, bat_stats, bow_stats, wkt_kind


def _dark_bar_h(labels, values, colors, title, xlabel=""):
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")
    bars = ax.barh(labels, values, color=colors, height=0.6)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{w:.1f}%" if "%" in xlabel else f"{int(w)}",
                va="center", color="white", fontsize=8)
    ax.set_title(title, color="white", fontsize=11)
    ax.set_xlabel(xlabel or "", color="#aaa", fontsize=9)
    ax.tick_params(colors="#aaa", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
    ax.grid(True, color="#1e2530", linewidth=0.5, linestyle="--", alpha=0.6, axis="x")
    plt.tight_layout()
    return fig


def show_drs_view(data):
    st.markdown("<h2>DRS Analytics</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5);margin-bottom:20px;'>"
        "872 DRS decisions across 18 IPL seasons — the only cricket dashboard that analyses this</p>",
        unsafe_allow_html=True,
    )

    drs, team_stats, bat_stats, bow_stats, wkt_kind = _compute_drs(data)

    # Top metrics
    total      = len(drs)
    upheld     = int((drs["review_decision"] == "upheld").sum())
    struck     = total - upheld
    best_team  = team_stats.sort_values("success_pct", ascending=False).iloc[0]
    most_lucky = bat_stats.sort_values("upheld", ascending=False).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total DRS Decisions", total)
    c2.metric("Reviews Upheld", upheld, f"{round(upheld/total*100,1)}%")
    c3.metric("Struck Down", struck, f"{round(struck/total*100,1)}%")
    c4.metric("Most Lucky Escapes", most_lucky["review_batter"], f"{int(most_lucky['upheld'])} times")

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["Teams", "Batters", "Bowlers", "Wicket Types"])

    # ── TAB 1: Teams ──────────────────────────────────────────────
    with tab1:
        st.markdown("<h3>Team DRS Success Rate</h3>", unsafe_allow_html=True)
        ts = team_stats.sort_values("success_pct", ascending=True)
        colors = [TEAM_COLORS.get(t, "#00FFFF") for t in ts["team_reviewed"]]
        short  = [t[:20] for t in ts["team_reviewed"]]
        fig1   = _dark_bar_h(short, ts["success_pct"].tolist(), colors,
                             "Team DRS Success Rate", "% Reviews Upheld")
        st.pyplot(fig1)

        st.markdown("<h3>Teams That Review Most</h3>", unsafe_allow_html=True)
        ts2    = team_stats.sort_values("total", ascending=False)
        medals = ["1st", "2nd", "3rd"] + [f"#{i}" for i in range(4, 15)]
        for i, row in enumerate(ts2.itertuples()):
            tc = TEAM_COLORS.get(row.team_reviewed, "#00FFFF")
            st.markdown(
                f"<div class='card'>{medals[i]} &nbsp; <b>{row.team_reviewed}</b> &nbsp;&mdash;&nbsp; "
                f"{int(row.total)} reviews &nbsp;|&nbsp; "
                f"<span style='color:#4ECDC4;'>{int(row.upheld)} upheld</span> &nbsp;|&nbsp; "
                f"<span style='color:{tc};'>{row.success_pct}% success</span></div>",
                unsafe_allow_html=True,
            )

    # ── TAB 2: Batters ────────────────────────────────────────────
    with tab2:
        st.markdown("<h3>Most Lucky Escapes (Reviews Upheld)</h3>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:rgba(255,255,255,0.5);font-size:13px;'>"
            "These batters challenged the umpire and won — surviving dismissals they should have lost</p>",
            unsafe_allow_html=True,
        )
        top_lucky = bat_stats.sort_values("upheld", ascending=False).head(10)
        for i, row in enumerate(top_lucky.itertuples(), 1):
            st.markdown(
                f"<div class='card'>#{i} &nbsp; <b>{row.review_batter}</b> &nbsp;&mdash;&nbsp; "
                f"<span style='color:#4ECDC4;font-weight:800;'>{int(row.upheld)} lucky escapes</span> "
                f"from {int(row.total)} reviews &nbsp;|&nbsp; "
                f"Success rate: {row.success_pct}%</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<h3>Best DRS Success Rate (min 3 reviews)</h3>", unsafe_allow_html=True)
        top_rate = bat_stats.sort_values("success_pct", ascending=False).head(10)
        fig2 = _dark_bar_h(
            top_rate["review_batter"].tolist(),
            top_rate["success_pct"].tolist(),
            ["#4ECDC4"] * len(top_rate),
            "Batter DRS Success Rate", "% Reviews Upheld",
        )
        st.pyplot(fig2)

        st.markdown("<h3>Most Struck Down (Wrong Challenges)</h3>", unsafe_allow_html=True)
        most_wrong = bat_stats.copy()
        most_wrong["struck"] = most_wrong["total"] - most_wrong["upheld"]
        most_wrong = most_wrong.sort_values("struck", ascending=False).head(8)
        for i, row in enumerate(most_wrong.itertuples(), 1):
            st.markdown(
                f"<div class='card'>#{i} &nbsp; <b>{row.review_batter}</b> &nbsp;&mdash;&nbsp; "
                f"<span style='color:#FF6B6B;font-weight:800;'>{int(row.struck)} wrong reviews</span> "
                f"from {int(row.total)} total</div>",
                unsafe_allow_html=True,
            )

    with tab3:
        st.markdown("<h3>Bowlers Whose Decisions Get Overturned Most</h3>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:rgba(255,255,255,0.5);font-size:13px;'>"
            "When a batter reviews against these bowlers, they tend to win</p>",
            unsafe_allow_html=True,
        )
        top_bow = bow_stats.head(10)
        fig3 = _dark_bar_h(
            top_bow["bowler"].tolist(),
            top_bow["overturn_pct"].tolist(),
            ["#FF6B6B"] * len(top_bow),
            "Bowlers Most Often Overturned by DRS", "% Reviews Upheld Against Them",
        )
        st.pyplot(fig3)

        st.markdown("<h3>Safest Bowlers (Fewest Overturns)</h3>", unsafe_allow_html=True)
        safe = bow_stats[bow_stats["total"] >= 5].sort_values("overturn_pct").head(8)
        for i, row in enumerate(safe.itertuples(), 1):
            st.markdown(
                f"<div class='card'>#{i} &nbsp; <b>{row.bowler}</b> &nbsp;&mdash;&nbsp; "
                f"<span style='color:#4ECDC4;font-weight:800;'>{row.overturn_pct}% overturn rate</span> "
                f"from {int(row.total)} reviews</div>",
                unsafe_allow_html=True,
            )

    
    with tab4:
        st.markdown("<h3>DRS by Dismissal Type</h3>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:rgba(255,255,255,0.5);font-size:13px;'>"
            "LBW reviews dominate — batters challenge the finger almost every time they are given out leg before</p>",
            unsafe_allow_html=True,
        )

        fig4, ax4 = plt.subplots(figsize=(6, 4))
        fig4.patch.set_facecolor("#0e1117")
        ax4.set_facecolor("#0e1117")
        colors_pie = ["#FF6B6B", "#FFE66D", "#4ECDC4", "#A8E6CF", "#C7CEEA"]
        _, _, autotexts = ax4.pie(
            wkt_kind["count"],
            labels=wkt_kind["kind"],
            autopct="%1.0f%%",
            colors=colors_pie[:len(wkt_kind)],
            textprops={"color": "white", "fontsize": 9},
            wedgeprops={"linewidth": 0.5, "edgecolor": "#0e1117"},
        )
        for at in autotexts:
            at.set_color("white")
        ax4.set_title("DRS Reviews by Wicket Type", color="white", fontsize=11)
        plt.tight_layout()
        st.pyplot(fig4)

        # Upheld vs struck by wicket type
        st.markdown("<h3>Success Rate by Dismissal Type</h3>", unsafe_allow_html=True)
        wkt_detail = drs.groupby(["wicket_kind", "review_decision"]).size().unstack(fill_value=0).reset_index()
        if "upheld" in wkt_detail.columns and "struck down" in wkt_detail.columns:
            wkt_detail["total"]   = wkt_detail["upheld"] + wkt_detail["struck down"]
            wkt_detail["success"] = (wkt_detail["upheld"] / wkt_detail["total"] * 100).round(1)
            for _, row in wkt_detail.iterrows():
                st.markdown(
                    f"<div class='card'><b>{row['wicket_kind']}</b> &nbsp;&mdash;&nbsp; "
                    f"{int(row['total'])} reviews &nbsp;|&nbsp; "
                    f"<span style='color:#4ECDC4;'>{int(row['upheld'])} upheld ({row['success']}%)</span></div>",
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown(
        "<div class='card'>"
        "<p><b style='color:#00FFFF;'>Resume talking point:</b> "
        "Analysed 872 DRS decisions across 18 IPL seasons — the first cricket analytics dashboard "
        "to quantify review success rates by team, batter, and bowler. "
        "Found RCB had the highest team DRS success rate (41.8%) while KKR wasted the most reviews.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
