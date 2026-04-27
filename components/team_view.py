import streamlit as st
import pandas as pd
from utils.chart_style import (
    dark_bar_chart, dark_pie_chart,
    team_color, sr_tag, ACCENT, ACCENT2, ACCENT3, DARK_BG, TEXT_COLOR
)
import matplotlib.pyplot as plt


def show_team_view(data):

    st.markdown("<h2 style='color:white;'>🏏 Team HQ</h2>", unsafe_allow_html=True)

    team = st.selectbox("Select Team", sorted(data["batting_team"].unique()))
    df   = data[data["batting_team"] == team]
    t_color = team_color(team)

    # ── compute stats ─────────────────────────────────────────────
    total_runs = int(df["runs_batter"].sum())
    balls      = int(df["balls_faced"].sum()) if "balls_faced" in df.columns else len(df)
    sr         = round(total_runs / balls * 100, 2) if balls > 0 else 0
    boundaries = int((df["runs_batter"] == 4).sum())
    sixes      = int((df["runs_batter"] == 6).sum())
    wickets    = int(df["player_dismissed"].notna().sum()) if "player_dismissed" in df.columns else 0
    dot_balls  = int((df["runs_batter"] == 0).sum())
    dot_pct    = round(dot_balls / balls * 100, 1) if balls > 0 else 0
    boundary_pct = round((boundaries + sixes) / balls * 100, 1) if balls > 0 else 0

    sr_emoji, sr_label = sr_tag(sr)

    # ── team header card ─────────────────────────────────────────
    st.markdown(f"""
    <div class="team-header" style="background: rgba(255,255,255,0.04);
         border-left: 5px solid {t_color};">
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:14px;">
            <div style="width:50px; height:50px; border-radius:50%;
                        background:{t_color}25; display:flex; align-items:center;
                        justify-content:center; font-size:22px; font-weight:800;
                        color:{t_color}; flex-shrink:0;">
                {team[:2].upper()}
            </div>
            <div>
                <p class="team-name-title">{team}</p>
                <span style="background:{t_color}20; color:{t_color};
                             border:1px solid {t_color}50; border-radius:99px;
                             font-size:11px; font-weight:700; padding:2px 10px;">
                    {sr_emoji} {sr_label}
                </span>
            </div>
        </div>

        <div>
            <div class="team-stat-row">
                <span class="team-stat-label">Runs Plundered</span>
                <span class="team-stat-value" style="color:{t_color};">{total_runs:,}</span>
            </div>
            <div class="team-stat-row">
                <span class="team-stat-label">Deliveries Faced</span>
                <span class="team-stat-value">{balls:,}</span>
            </div>
            <div class="team-stat-row">
                <span class="team-stat-label">Strike Rate</span>
                <span class="team-stat-value">{sr}</span>
            </div>
            <div class="team-stat-row">
                <span class="team-stat-label">Wickets Lost</span>
                <span class="team-stat-value">{wickets}</span>
            </div>
            <div class="team-stat-row">
                <span class="team-stat-label">Fours / Sixes</span>
                <span class="team-stat-value">{boundaries} / {sixes}</span>
            </div>
            <div class="team-stat-row">
                <span class="team-stat-label">Boundary %</span>
                <span class="team-stat-value">{boundary_pct}%</span>
            </div>
            <div class="team-stat-row">
                <span class="team-stat-label">Dot Ball %</span>
                <span class="team-stat-value">{dot_pct}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── run composition pie ───────────────────────────────────────
    st.markdown(
        "<h3 style='color:white; margin:20px 0 10px;'>🎯 How Runs Are Scored</h3>",
        unsafe_allow_html=True,
    )
    boundary_runs = boundaries * 4 + sixes * 6
    running_runs  = total_runs - boundary_runs
    fig_pie = dark_pie_chart(
        ["From Boundaries", "Running Between Wickets"],
        [boundary_runs, max(running_runs, 0)],
        title=f"{team} — Run Composition",
        colors=[t_color, "#444"],
    )
    st.pyplot(fig_pie)

    # ── top batters bar ───────────────────────────────────────────
    st.markdown(
        "<h3 style='color:white; margin:20px 0 10px;'>🔥 Top Run Scorers</h3>",
        unsafe_allow_html=True,
    )
    top_batters = (
        df.groupby("batter")["runs_batter"].sum()
        .sort_values(ascending=False).head(8)
    )

    for i, (player, p_runs) in enumerate(top_batters.items(), 1):
        p_balls  = int(df[df["batter"] == player]["balls_faced"].sum())
        p_sr     = round(p_runs / p_balls * 100, 1) if p_balls > 0 else 0
        bar_pct  = int(p_runs / top_batters.iloc[0] * 100)
        medal    = ["🥇","🥈","🥉"][i-1] if i <= 3 else f"#{i}"
        st.markdown(f"""
        <div class="team-player-card">
            <div style="display:flex; align-items:center; gap:12px;">
                <span class="team-rank">{medal}</span>
                <div>
                    <div class="team-player-name">{player}</div>
                    <div class="team-player-stat">SR: {p_sr}</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:16px; font-weight:800; color:{t_color};">{p_runs:,}</div>
                <div style="font-size:11px; color:rgba(255,255,255,0.3); margin-top:2px;">runs</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── runs by over phase bar chart ──────────────────────────────
    st.markdown(
        "<h3 style='color:white; margin:20px 0 10px;'>⏱️ Runs by Over Phase</h3>",
        unsafe_allow_html=True,
    )
    df2 = df.copy()
    df2["phase"] = pd.cut(
        df2["over"], bins=[-1, 5, 14, 19],
        labels=["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"],
    )
    phase_runs = df2.groupby("phase", observed=True)["runs_batter"].sum()

    fig_phase = dark_bar_chart(
        list(phase_runs.index.astype(str)),
        list(phase_runs.values),
        title=f"{team} — Runs by Over Phase",
        ylabel="Total Runs",
        color=t_color,
        highlight_max=True,
        figsize=(8, 4),
    )
    st.pyplot(fig_phase)

    # ── most aggressive batters ───────────────────────────────────
    st.markdown(
        "<h3 style='color:white; margin:20px 0 10px;'>🚀 Most Aggressive Batters (min 200 balls)</h3>",
        unsafe_allow_html=True,
    )
    agg = df.groupby("batter").agg(
        runs=("runs_batter", "sum"),
        balls=("balls_faced", "sum"),
    )
    agg = agg[agg["balls"] >= 200].copy()
    if not agg.empty:
        agg["sr"] = (agg["runs"] / agg["balls"] * 100).round(1)
        top_sr = agg.sort_values("sr", ascending=False).head(5)
        for i, (player, row) in enumerate(top_sr.iterrows(), 1):
            sr_e, sr_l = sr_tag(row["sr"])
            st.markdown(f"""
            <div class="team-player-card">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span class="team-rank">#{i}</span>
                    <div>
                        <div class="team-player-name">{player}</div>
                        <div class="team-player-stat">{sr_e} {sr_l}</div>
                    </div>
                </div>
                <div style="font-size:16px; font-weight:800; color:{ACCENT2};">SR {row['sr']}</div>
            </div>
            """, unsafe_allow_html=True)
