import streamlit as st
import pandas as pd
from utils.analysis import player_stats, player_trend
from utils.chart_style import (
    dark_line_chart, dark_bar_chart, dark_pie_chart,
    sr_tag, runs_tag, team_color, ACCENT, ACCENT2, ACCENT3
)


def _initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()


def _batting_role(bat_pos_series):
    avg_pos = bat_pos_series.mean()
    if avg_pos <= 2:   return ("Opener", "#00FFFF")
    if avg_pos <= 5:   return ("Middle Order", "#FFE66D")
    return ("Finisher", "#FF6B6B")


def show_player_view(data):

    st.markdown("<h2 style='color:white;'>📊 Batter Profiles</h2>", unsafe_allow_html=True)

    player = st.selectbox("Select Batter", sorted(data["batter"].unique()))

    runs, sr = player_stats(data, player)
    player_df = data[data["batter"] == player]

    # ── compute extended stats ────────────────────────────────────
    total_balls   = int(player_df["balls_faced"].sum())
    total_fours   = int((player_df["runs_batter"] == 4).sum())
    total_sixes   = int((player_df["runs_batter"] == 6).sum())
    dot_balls     = int((player_df["runs_batter"] == 0).sum())
    dot_pct       = round(dot_balls / total_balls * 100, 1) if total_balls > 0 else 0

    # Dismissals
    if "player_dismissed" in data.columns:
        dismissals = int(player_df["player_dismissed"].notna().sum())
    else:
        dismissals = 0
    avg = round(runs / dismissals, 2) if dismissals > 0 else runs

    # Batting role from average position
    role_name, role_color = _batting_role(player_df["bat_pos"])

    # Primary team (most balls faced for)
    primary_team = player_df["batting_team"].value_counts().index[0] if len(player_df) > 0 else ""
    t_color = team_color(primary_team)

    # Commentary tags
    sr_emoji, sr_label   = sr_tag(sr)
    runs_emoji, runs_label = runs_tag(runs)

    # Initials avatar
    initials = _initials(player)

    # ── profile card ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="player-profile-card" style="background: rgba(255,255,255,0.04);
         border-left: 4px solid {t_color};">

        <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px;">
            <div class="player-avatar" style="background:{t_color}20; color:{t_color};">
                {initials}
            </div>
            <div>
                <p class="player-name">{player}</p>
                <div>
                    <span class="role-badge"
                          style="background:{role_color}20; color:{role_color};
                                 border:1px solid {role_color}50;">
                        {role_name}
                    </span>
                    &nbsp;
                    <span class="role-badge"
                          style="background:{t_color}20; color:{t_color};
                                 border:1px solid {t_color}50;">
                        {primary_team}
                    </span>
                </div>
            </div>
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:16px;">
            <span class="commentary-tag">{runs_emoji} {runs_label}</span>
            <span class="commentary-tag">{sr_emoji} {sr_label}</span>
            <span class="commentary-tag">💥 {total_sixes} Sixes</span>
            <span class="commentary-tag">🏏 {total_fours} Fours</span>
        </div>

        <div>
            <div class="stat-row">
                <span class="stat-label">Runs Plundered</span>
                <span class="stat-value" style="color:{t_color};">{int(runs):,}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Deliveries Faced</span>
                <span class="stat-value">{total_balls:,}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Strike Rate</span>
                <span class="stat-value">{round(sr, 2)}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Batting Average</span>
                <span class="stat-value">{avg}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Boundary %</span>
                <span class="stat-value">{round((total_fours + total_sixes) / total_balls * 100, 1) if total_balls > 0 else 0}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Dot Ball %</span>
                <span class="stat-value">{dot_pct}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── run trend chart ───────────────────────────────────────────
    st.markdown(
        f"<h3 style='color:white; margin:20px 0 10px;'>📈 Match-by-Match Runs — {player}</h3>",
        unsafe_allow_html=True,
    )
    trend = player_trend(data, player)
    if not trend.empty:
        fig = dark_line_chart(
            trend.index, trend,
            title=f"{player} — Runs per Match",
            xlabel="Match", ylabel="Runs",
            color=t_color,
        )
        st.pyplot(fig)

    # ── run distribution chart ────────────────────────────────────
    st.markdown(
        "<h3 style='color:white; margin:20px 0 10px;'>🎯 How Runs Are Scored</h3>",
        unsafe_allow_html=True,
    )

    run_dist = player_df["runs_batter"].value_counts().sort_index()
    # Simplify: 0,1,2,3,4,6
    buckets = {
        "Dots (0)": int((player_df["runs_batter"] == 0).sum()),
        "Singles (1)": int((player_df["runs_batter"] == 1).sum()),
        "Twos (2)":  int((player_df["runs_batter"] == 2).sum()),
        "Threes (3)": int((player_df["runs_batter"] == 3).sum()),
        "Fours (4)": total_fours,
        "Sixes (6)": total_sixes,
    }
    fig2 = dark_pie_chart(
        list(buckets.keys()),
        list(buckets.values()),
        title=f"{player} — Ball Outcome Distribution",
        colors=["#555", "#4ECDC4", "#45B7D1", "#96CEB4", ACCENT, ACCENT2],
    )
    st.pyplot(fig2)

    # ── dismissal type breakdown ──────────────────────────────────
    if "wicket_kind" in data.columns:
        dismissed = data[
            (data["player_dismissed"] == player) & data["wicket_kind"].notna()
        ] if "player_dismissed" in data.columns else pd.DataFrame()

        if not dismissed.empty:
            st.markdown(
                "<h3 style='color:white; margin:20px 0 10px;'>🎳 How Does This Batter Get Out?</h3>",
                unsafe_allow_html=True,
            )
            wkt_counts = dismissed["wicket_kind"].value_counts()
            fig3 = dark_pie_chart(
                list(wkt_counts.index),
                list(wkt_counts.values),
                title=f"{player} — Dismissal Types",
                colors=[ACCENT3, ACCENT2, ACCENT, "#A8E6CF", "#C7CEEA", "#FF8B94"],
            )
            st.pyplot(fig3)

    # ── phase breakdown ───────────────────────────────────────────
    st.markdown(
        "<h3 style='color:white; margin:20px 0 10px;'>⏱️ Performance by Over Phase</h3>",
        unsafe_allow_html=True,
    )
    player_df = player_df.copy()
    player_df["phase"] = pd.cut(
        player_df["over"],
        bins=[-1, 5, 14, 19],
        labels=["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"],
    )
    phase_stats = player_df.groupby("phase", observed=True).agg(
        runs=("runs_batter", "sum"),
        balls=("balls_faced", "sum"),
    ).reset_index()
    phase_stats["sr"] = (phase_stats["runs"] / phase_stats["balls"] * 100).round(1)

    fig4 = dark_bar_chart(
        list(phase_stats["phase"].astype(str)),
        list(phase_stats["sr"]),
        title=f"{player} — Strike Rate by Phase",
        ylabel="Strike Rate",
        color=t_color,
        highlight_max=True,
        figsize=(8, 4),
    )
    st.pyplot(fig4)
