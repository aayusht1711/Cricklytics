import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ── CONSTANTS ────────────────────────────────────────────────────
DARK_BG = "#0e1117"
ACCENT = "#00FFFF"
ACCENT2 = "#FFE66D"
ACCENT3 = "#FF6B6B"
TEXT_COLOR = "#e0e0e0"

TEAM_COLORS = {
    "Mumbai Indians": "#005DA0", "Chennai Super Kings": "#F7C010",
    "Royal Challengers Bangalore": "#EC1C24", "Royal Challengers Bengaluru": "#EC1C24",
    "Kolkata Knight Riders": "#3A225D", "Rajasthan Royals": "#EA1A85",
    "Sunrisers Hyderabad": "#F7700E", "Delhi Daredevils": "#0078BC",
    "Delhi Capitals": "#0078BC", "Kings XI Punjab": "#DCDDDF",
    "Punjab Kings": "#ED1B24", "Deccan Chargers": "#FDB933",
    "Gujarat Titans": "#1C4966", "Lucknow Super Giants": "#A72056",
}

PRESSURE_COLORS = {"Low": "#4ECDC4", "Medium": "#FFE66D", "High": "#FF6B6B"}


# ── PRESSURE COMPUTATION (cached) ───────────────────────────────
@st.cache_data
def _compute_pressure_index(data):
    """Assign a pressure score (0–100) to every delivery."""
    df = data.copy()

    # --- Compute innings-1 totals (targets) per match ---
    inn1 = df[df["innings"] == 1]
    targets = (
        inn1.groupby("match_id")["team_runs"]
        .max()
        .reset_index()
        .rename(columns={"team_runs": "inn1_total"})
    )
    targets["target"] = targets["inn1_total"] + 1

    df = df.merge(targets[["match_id", "target"]], on="match_id", how="left")
    df["target"] = df["target"].fillna(0).astype(int)

    # --- Total valid balls in the innings for balls-remaining calc ---
    inn2_max = (
        df[df["innings"] == 2]
        .groupby("match_id")
        .agg(total_balls=("valid_ball", "sum"))
        .reset_index()
    )
    df = df.merge(inn2_max, on="match_id", how="left", suffixes=("", "_inn2"))
    df["total_balls"] = df["total_balls"].fillna(120).astype(int)

    # --- Cumulative valid balls so far in each innings ---
    df = df.sort_values(["match_id", "innings", "over", "ball"])
    df["cum_valid"] = df.groupby(["match_id", "innings"])["valid_ball"].cumsum()

    # --- Pressure calculation ---
    pressure = np.full(len(df), 10.0)

    # Masks
    inn2_mask = df["innings"].values == 2
    inn1_mask = df["innings"].values == 1

    team_wkts = df["team_wickets"].values.astype(float)
    overs = df["over"].values.astype(float)
    team_runs = df["team_runs"].values.astype(float)
    target_arr = df["target"].values.astype(float)
    cum_valid = df["cum_valid"].values.astype(float)

    # ========== INNINGS 2 (chasing) ==========
    base_inn2 = 20.0
    pressure[inn2_mask] = base_inn2

    # Wickets pressure
    pressure[inn2_mask] += team_wkts[inn2_mask] * 8

    # Required run rate pressure
    balls_remaining = np.maximum(120 - cum_valid, 1)
    runs_needed = target_arr - team_runs
    required_rr = np.where(
        balls_remaining > 0,
        runs_needed / (balls_remaining / 6),
        0,
    )
    rr_gap = np.maximum(required_rr - 8, 0)
    pressure[inn2_mask] += rr_gap[inn2_mask] * 4

    # Death over bonus (overs 16–20, 0-indexed over >= 15)
    death_mask_inn2 = inn2_mask & (overs >= 15)
    pressure[death_mask_inn2] += 15

    # Close match bonus (within 40 runs in last 5 overs)
    close_mask = inn2_mask & (overs >= 15) & (runs_needed <= 40) & (runs_needed > 0)
    pressure[close_mask] += 12

    # ========== INNINGS 1 (setting) ==========
    pressure[inn1_mask] = 10.0
    pressure[inn1_mask] += team_wkts[inn1_mask] * 6
    death_mask_inn1 = inn1_mask & (overs >= 15)
    pressure[death_mask_inn1] += 10

    # Collapse bonus: 3+ wickets fallen and deep overs
    pressure_collapse = inn1_mask & (team_wkts >= 3) & (overs >= 10)
    pressure[pressure_collapse] += 8

    # Cap at 100
    pressure = np.clip(pressure, 0, 100)

    df["pressure"] = pressure.round(1)

    # Pressure category
    df["pressure_cat"] = pd.cut(
        df["pressure"],
        bins=[-1, 30, 60, 101],
        labels=["Low", "Medium", "High"],
    )

    return df


@st.cache_data
def _batter_clutch_leaderboard(df_pressure):
    """Compute clutch scores for batters. Min 500 balls faced."""
    batters = (
        df_pressure.groupby("batter")
        .agg(
            total_balls=("valid_ball", "sum"),
            matches=("match_id", "nunique"),
            team=("batting_team", lambda x: x.value_counts().index[0]),
        )
        .reset_index()
    )
    batters = batters[batters["total_balls"] >= 500]

    # High-pressure stats
    hp = df_pressure[df_pressure["pressure"] >= 60].copy()
    hp_stats = (
        hp.groupby("batter")
        .agg(
            hp_balls=("valid_ball", "sum"),
            hp_runs=("runs_batter", "sum"),
            hp_boundaries=("runs_batter", lambda x: ((x == 4) | (x == 6)).sum()),
        )
        .reset_index()
    )

    merged = batters.merge(hp_stats, on="batter", how="left").fillna(0)
    merged["hp_balls"] = merged["hp_balls"].astype(int)
    merged["hp_runs"] = merged["hp_runs"].astype(int)

    merged["hp_sr"] = np.where(
        merged["hp_balls"] > 0,
        (merged["hp_runs"] / merged["hp_balls"] * 100).round(1),
        0,
    )
    merged["hp_boundary_pct"] = np.where(
        merged["hp_balls"] > 0,
        (merged["hp_boundaries"] / merged["hp_balls"] * 100).round(1),
        0,
    )

    # Clutch Score = (SR_hp / 100) * 0.6  +  (boundary%_hp) * 0.4
    merged["clutch_score"] = (
        (merged["hp_sr"] / 100) * 0.6 + (merged["hp_boundary_pct"]) * 0.4
    ).round(2)

    merged = merged[merged["hp_balls"] >= 30]  # need some HP exposure
    merged = merged.sort_values("clutch_score", ascending=False).reset_index(drop=True)

    return merged


@st.cache_data
def _bowler_clutch_leaderboard(df_pressure):
    """Compute clutch scores for bowlers. Min 300 balls bowled."""
    bowlers = (
        df_pressure.groupby("bowler")
        .agg(
            total_balls=("valid_ball", "sum"),
            matches=("match_id", "nunique"),
            team=("bowling_team", lambda x: x.value_counts().index[0]),
        )
        .reset_index()
    )
    bowlers = bowlers[bowlers["total_balls"] >= 300]

    hp = df_pressure[df_pressure["pressure"] >= 60].copy()
    hp_stats = (
        hp.groupby("bowler")
        .agg(
            hp_balls=("valid_ball", "sum"),
            hp_runs=("runs_total", "sum"),
            hp_dots=("runs_batter", lambda x: (x == 0).sum()),
        )
        .reset_index()
    )

    merged = bowlers.merge(hp_stats, on="bowler", how="left").fillna(0)
    merged["hp_balls"] = merged["hp_balls"].astype(int)
    merged["hp_runs"] = merged["hp_runs"].astype(int)

    merged["hp_economy"] = np.where(
        merged["hp_balls"] > 0,
        (merged["hp_runs"] / merged["hp_balls"] * 6).round(2),
        99,
    )
    merged["hp_dot_pct"] = np.where(
        merged["hp_balls"] > 0,
        (merged["hp_dots"] / merged["hp_balls"] * 100).round(1),
        0,
    )

    # Clutch Score = dot_ball%_hp * 0.5  +  max(0, 15 - economy_hp) * 0.5
    econ_component = np.clip(15 - merged["hp_economy"], 0, 15)
    merged["clutch_score"] = (
        merged["hp_dot_pct"] * 0.5 + econ_component * 0.5
    ).round(2)

    merged = merged[merged["hp_balls"] >= 20]
    merged = merged.sort_values("clutch_score", ascending=False).reset_index(drop=True)

    return merged


@st.cache_data
def _player_pressure_profile(df_pressure, player):
    """Split stats for a player across Low / Medium / High pressure."""
    pdf = df_pressure[df_pressure["batter"] == player]
    if pdf.empty:
        return None

    results = {}
    for cat in ["Low", "Medium", "High"]:
        cat_df = pdf[pdf["pressure_cat"] == cat]
        balls = int(cat_df["valid_ball"].sum())
        runs = int(cat_df["runs_batter"].sum())
        dismissals = int(cat_df["player_dismissed"].notna().sum()) if "player_dismissed" in cat_df.columns else 0
        fours = int((cat_df["runs_batter"] == 4).sum())
        sixes = int((cat_df["runs_batter"] == 6).sum())
        dots = int((cat_df["runs_batter"] == 0).sum())

        sr = round(runs / balls * 100, 1) if balls > 0 else 0
        avg = round(runs / dismissals, 1) if dismissals > 0 else runs
        boundary_pct = round((fours + sixes) / balls * 100, 1) if balls > 0 else 0
        dot_pct = round(dots / balls * 100, 1) if balls > 0 else 0

        results[cat] = {
            "balls": balls,
            "runs": runs,
            "sr": sr,
            "avg": avg,
            "boundary_pct": boundary_pct,
            "dot_pct": dot_pct,
            "fours": fours,
            "sixes": sixes,
        }

    return results


@st.cache_data
def _clutch_moments(df_pressure):
    """Top individual match performances under high pressure (>= 60)."""
    hp = df_pressure[(df_pressure["pressure"] >= 60) & (df_pressure["innings"].isin([1, 2]))]

    match_perf = (
        hp.groupby(["match_id", "batter", "batting_team", "bowling_team", "season"])
        .agg(
            hp_runs=("runs_batter", "sum"),
            hp_balls=("valid_ball", "sum"),
            hp_fours=("runs_batter", lambda x: (x == 4).sum()),
            hp_sixes=("runs_batter", lambda x: (x == 6).sum()),
        )
        .reset_index()
    )
    match_perf = match_perf[match_perf["hp_runs"] >= 20]
    match_perf["hp_sr"] = (match_perf["hp_runs"] / match_perf["hp_balls"] * 100).round(1)
    match_perf = match_perf.sort_values("hp_runs", ascending=False).head(15).reset_index(drop=True)

    return match_perf


@st.cache_data
def _scatter_data(df_pressure):
    """Aggregate data for pressure vs performance scatter."""
    # Only batters with 200+ balls
    batter_total = (
        df_pressure.groupby("batter")
        .agg(total_balls=("valid_ball", "sum"), team=("batting_team", lambda x: x.value_counts().index[0]))
        .reset_index()
    )
    batter_total = batter_total[batter_total["total_balls"] >= 200]

    avg_pressure = (
        df_pressure.groupby("batter")["pressure"].mean().round(1).reset_index()
    )
    avg_pressure.columns = ["batter", "avg_pressure"]

    hp = df_pressure[df_pressure["pressure"] >= 60]
    hp_sr = (
        hp.groupby("batter")
        .agg(hp_runs=("runs_batter", "sum"), hp_balls=("valid_ball", "sum"))
        .reset_index()
    )
    hp_sr["hp_sr"] = np.where(hp_sr["hp_balls"] > 0, (hp_sr["hp_runs"] / hp_sr["hp_balls"] * 100).round(1), 0)

    merged = batter_total.merge(avg_pressure, on="batter").merge(hp_sr[["batter", "hp_sr", "hp_balls"]], on="batter", how="left")
    merged = merged.fillna(0)
    merged = merged[merged["hp_balls"] >= 20]

    return merged


# ── PLOTLY LAYOUT HELPER ─────────────────────────────────────────
def _plotly_dark_layout(fig, title="", xaxis_title="", yaxis_title="", height=500):
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT_COLOR, size=16)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT_COLOR,
        xaxis=dict(
            title=xaxis_title,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
        ),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor="#1a1f2a", font_color="white"),
    )
    return fig


# ── CARD HELPERS ─────────────────────────────────────────────────
def _glass_card(content, border_color=ACCENT, extra_style=""):
    return f"""
<div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:20px;
border-left:4px solid {border_color};backdrop-filter:blur(10px);
margin-bottom:12px;{extra_style}'>
{content}
</div>
"""


def _metric_mini(label, value, color=ACCENT):
    return f"""
<div style='text-align:center;'>
<div style='color:rgba(255,255,255,0.5);font-size:11px;text-transform:uppercase;
letter-spacing:1px;margin-bottom:4px;'>{label}</div>
<div style='color:{color};font-size:22px;font-weight:700;'>{value}</div>
</div>
"""


# ── MAIN VIEW ────────────────────────────────────────────────────
def show_clutch_view(data):
    # Inject CSS animations
    st.markdown("""
<style>
@keyframes fadeInUp {
from { opacity:0; transform:translateY(20px); }
to   { opacity:1; transform:translateY(0); }
}
.clutch-header {
background: linear-gradient(135deg, rgba(255,107,107,0.15), rgba(0,255,255,0.10));
border-radius: 16px; padding: 28px 32px; margin-bottom: 24px;
border: 1px solid rgba(255,255,255,0.06);
animation: fadeInUp 0.6s ease;
}
.clutch-header h2 { margin:0; font-size:28px; }
.clutch-header p  { color:rgba(255,255,255,0.6); margin:6px 0 0; font-size:14px; }
.moment-card {
background:rgba(255,255,255,0.04); border-radius:12px; padding:18px 20px;
border-left:4px solid #FF6B6B; margin-bottom:10px;
backdrop-filter:blur(10px);
animation: fadeInUp 0.5s ease;
}
.rank-badge {
display:inline-block; width:28px; height:28px; line-height:28px;
text-align:center; border-radius:50%; font-weight:700; font-size:13px;
margin-right:10px;
}
</style>
""", unsafe_allow_html=True)

    # ── Header ──
    st.markdown("""
<div class='clutch-header'>
<h2>⚡ Clutch Factor &amp; Pressure Index</h2>
<p>Ranking players by performance under pressure — every delivery gets a
dynamic pressure score based on match situation, required rate, wickets fallen,
and game phase.</p>
</div>
""", unsafe_allow_html=True)

    # ── Compute pressure for all deliveries ──
    df_p = _compute_pressure_index(data)

    # ── 4-Tab Layout ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Clutch Leaderboard",
        "📊 Player Pressure Profile",
        "🔥 Most Clutch Moments",
        "🎯 Pressure vs Performance",
    ])

    # ================================================================
    # TAB 1 — CLUTCH LEADERBOARD
    # ================================================================
    with tab1:
        role = st.radio("Select Role", ["Batters", "Bowlers"], horizontal=True, key="clutch_role")

        if role == "Batters":
            lb = _batter_clutch_leaderboard(df_p)
            top = lb.head(20).copy()
            if top.empty:
                st.info("Not enough data to build the batter leaderboard.")
                return

            max_cs = top["clutch_score"].max()

            st.markdown(f"""
<div style='margin:16px 0 8px;color:rgba(255,255,255,0.5);font-size:12px;'>
Showing top {len(top)} batters · Min 500 balls faced · Clutch Score =
(HP Strike Rate / 100) × 0.6 + (HP Boundary%) × 0.4
</div>
""", unsafe_allow_html=True)

            # Build HTML table
            rows_html = ""
            for i, r in enumerate(top.itertuples(), 1):
                t_color = TEAM_COLORS.get(r.team, ACCENT)
                bar_width = max(5, int(r.clutch_score / max(max_cs, 1) * 100))

                if i <= 3:
                    badge_bg = ["#FFD700", "#C0C0C0", "#CD7F32"][i - 1]
                    badge = f"<span class='rank-badge' style='background:{badge_bg};color:#000;'>{i}</span>"
                else:
                    badge = f"<span class='rank-badge' style='background:rgba(255,255,255,0.08);color:{TEXT_COLOR};'>{i}</span>"

                rows_html += f"""
<div style='display:flex;align-items:center;padding:10px 16px;
border-bottom:1px solid rgba(255,255,255,0.04);'>
<div style='width:40px;flex-shrink:0;'>{badge}</div>
<div style='flex:1;'>
<span style='font-weight:600;color:white;'>{r.batter}</span>
<span style='color:{t_color};font-size:11px;margin-left:8px;'>{r.team}</span>
</div>
<div style='width:200px;margin:0 16px;'>
<div style='background:rgba(255,255,255,0.06);border-radius:6px;height:10px;overflow:hidden;'>
<div style='width:{bar_width}%;height:100%;border-radius:6px;
background:linear-gradient(90deg,{ACCENT},{ACCENT3});'></div>
</div>
</div>
<div style='width:60px;text-align:right;font-weight:700;color:{ACCENT};font-size:15px;'>
{r.clutch_score}
</div>
<div style='width:80px;text-align:center;color:rgba(255,255,255,0.5);font-size:12px;'>
SR {r.hp_sr}
</div>
<div style='width:60px;text-align:center;color:rgba(255,255,255,0.5);font-size:12px;'>
{r.hp_balls} HP
</div>
<div style='width:60px;text-align:center;color:rgba(255,255,255,0.5);font-size:12px;'>
{r.matches} M
</div>
</div>
"""

            st.markdown(_glass_card(f"""
<div style='font-size:12px;display:flex;padding:6px 16px;color:rgba(255,255,255,0.35);
border-bottom:1px solid rgba(255,255,255,0.06);font-weight:600;'>
<div style='width:40px;'>#</div>
<div style='flex:1;'>Player</div>
<div style='width:200px;text-align:center;'>Clutch Bar</div>
<div style='width:60px;text-align:right;'>Score</div>
<div style='width:80px;text-align:center;'>HP SR</div>
<div style='width:60px;text-align:center;'>HP Balls</div>
<div style='width:60px;text-align:center;'>Matches</div>
</div>
{rows_html}
""", border_color=ACCENT), unsafe_allow_html=True)

        else:  # Bowlers
            lb = _bowler_clutch_leaderboard(df_p)
            top = lb.head(20).copy()
            if top.empty:
                st.info("Not enough data to build the bowler leaderboard.")
                return

            max_cs = top["clutch_score"].max()

            st.markdown(f"""
<div style='margin:16px 0 8px;color:rgba(255,255,255,0.5);font-size:12px;'>
Showing top {len(top)} bowlers · Min 300 balls bowled · Clutch Score =
(HP Dot%) × 0.5 + (15 − HP Economy) × 0.5
</div>
""", unsafe_allow_html=True)

            rows_html = ""
            for i, r in enumerate(top.itertuples(), 1):
                t_color = TEAM_COLORS.get(r.team, ACCENT)
                bar_width = max(5, int(r.clutch_score / max(max_cs, 1) * 100))

                if i <= 3:
                    badge_bg = ["#FFD700", "#C0C0C0", "#CD7F32"][i - 1]
                    badge = f"<span class='rank-badge' style='background:{badge_bg};color:#000;'>{i}</span>"
                else:
                    badge = f"<span class='rank-badge' style='background:rgba(255,255,255,0.08);color:{TEXT_COLOR};'>{i}</span>"

                rows_html += f"""
<div style='display:flex;align-items:center;padding:10px 16px;
border-bottom:1px solid rgba(255,255,255,0.04);'>
<div style='width:40px;flex-shrink:0;'>{badge}</div>
<div style='flex:1;'>
<span style='font-weight:600;color:white;'>{r.bowler}</span>
<span style='color:{t_color};font-size:11px;margin-left:8px;'>{r.team}</span>
</div>
<div style='width:200px;margin:0 16px;'>
<div style='background:rgba(255,255,255,0.06);border-radius:6px;height:10px;overflow:hidden;'>
<div style='width:{bar_width}%;height:100%;border-radius:6px;
background:linear-gradient(90deg,{ACCENT2},{ACCENT3});'></div>
</div>
</div>
<div style='width:60px;text-align:right;font-weight:700;color:{ACCENT2};font-size:15px;'>
{r.clutch_score}
</div>
<div style='width:80px;text-align:center;color:rgba(255,255,255,0.5);font-size:12px;'>
Econ {r.hp_economy}
</div>
<div style='width:70px;text-align:center;color:rgba(255,255,255,0.5);font-size:12px;'>
Dot {r.hp_dot_pct}%
</div>
<div style='width:60px;text-align:center;color:rgba(255,255,255,0.5);font-size:12px;'>
{r.matches} M
</div>
</div>
"""

            st.markdown(_glass_card(f"""
<div style='font-size:12px;display:flex;padding:6px 16px;color:rgba(255,255,255,0.35);
border-bottom:1px solid rgba(255,255,255,0.06);font-weight:600;'>
<div style='width:40px;'>#</div>
<div style='flex:1;'>Bowler</div>
<div style='width:200px;text-align:center;'>Clutch Bar</div>
<div style='width:60px;text-align:right;'>Score</div>
<div style='width:80px;text-align:center;'>HP Econ</div>
<div style='width:70px;text-align:center;'>HP Dot%</div>
<div style='width:60px;text-align:center;'>Matches</div>
</div>
{rows_html}
""", border_color=ACCENT2), unsafe_allow_html=True)

    # ================================================================
    # TAB 2 — PLAYER PRESSURE PROFILE
    # ================================================================
    with tab2:
        all_batters = sorted(df_p["batter"].unique())
        selected = st.selectbox("Select Player", all_batters, key="clutch_player")

        profile = _player_pressure_profile(df_p, selected)
        if profile is None:
            st.warning("No data available for this player.")
        else:
            # Primary team for color
            p_team = df_p[df_p["batter"] == selected]["batting_team"].value_counts().index[0]
            p_color = TEAM_COLORS.get(p_team, ACCENT)

            st.markdown(f"""
<div style='margin:8px 0 16px;'>
<span style='font-size:20px;font-weight:700;color:white;'>{selected}</span>
<span style='color:{p_color};font-size:13px;margin-left:10px;'>{p_team}</span>
</div>
""", unsafe_allow_html=True)

            # Three pressure cards side-by-side
            cols = st.columns(3)
            for idx, cat in enumerate(["Low", "Medium", "High"]):
                s = profile[cat]
                emoji = ["🟢", "🟡", "🔴"][idx]
                color = PRESSURE_COLORS[cat]
                with cols[idx]:
                    st.markdown(_glass_card(f"""
<div style='text-align:center;'>
<div style='font-size:18px;font-weight:700;color:{color};margin-bottom:8px;'>
{emoji} {cat} Pressure
</div>
<div style='color:rgba(255,255,255,0.4);font-size:11px;margin-bottom:12px;'>
{s['balls']} balls · {s['runs']} runs
</div>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;'>
{_metric_mini("Strike Rate", s['sr'], color)}
{_metric_mini("Average", s['avg'], color)}
{_metric_mini("Boundary %", f"{s['boundary_pct']}%", color)}
{_metric_mini("Dot Ball %", f"{s['dot_pct']}%", color)}
</div>
</div>
""", border_color=color), unsafe_allow_html=True)

            # Bar chart comparing SR across pressure levels
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            categories = ["🟢 Low", "🟡 Medium", "🔴 High"]
            sr_vals = [profile[c]["sr"] for c in ["Low", "Medium", "High"]]
            boundary_vals = [profile[c]["boundary_pct"] for c in ["Low", "Medium", "High"]]
            dot_vals = [profile[c]["dot_pct"] for c in ["Low", "Medium", "High"]]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Strike Rate",
                x=categories, y=sr_vals,
                marker_color=[PRESSURE_COLORS["Low"], PRESSURE_COLORS["Medium"], PRESSURE_COLORS["High"]],
                text=[f"{v}" for v in sr_vals],
                textposition="outside",
                textfont=dict(color=TEXT_COLOR),
            ))
            fig.add_trace(go.Bar(
                name="Boundary %",
                x=categories, y=boundary_vals,
                marker_color=["rgba(78,205,196,0.5)", "rgba(255,230,109,0.5)", "rgba(255,107,107,0.5)"],
                text=[f"{v}%" for v in boundary_vals],
                textposition="outside",
                textfont=dict(color=TEXT_COLOR),
            ))

            _plotly_dark_layout(fig,
                title=f"{selected} — Performance Across Pressure Levels",
                xaxis_title="Pressure Category",
                yaxis_title="Value",
                height=420,
            )
            fig.update_layout(barmode="group", legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(color=TEXT_COLOR),
            ))
            st.plotly_chart(fig, use_container_width=True)

            # Dot ball % comparison (inverted bar — lower is better)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=categories, y=dot_vals,
                marker_color=[PRESSURE_COLORS["Low"], PRESSURE_COLORS["Medium"], PRESSURE_COLORS["High"]],
                text=[f"{v}%" for v in dot_vals],
                textposition="outside",
                textfont=dict(color=TEXT_COLOR),
            ))
            _plotly_dark_layout(fig2,
                title=f"{selected} — Dot Ball % Under Pressure",
                xaxis_title="Pressure Category",
                yaxis_title="Dot Ball %",
                height=350,
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ================================================================
    # TAB 3 — MOST CLUTCH MOMENTS
    # ================================================================
    with tab3:
        st.markdown("""
<div style='color:rgba(255,255,255,0.5);font-size:13px;margin-bottom:16px;'>
Top individual match performances where a batter scored 20+ runs on deliveries
with pressure ≥ 60. These are the moments that define legends.
</div>
""", unsafe_allow_html=True)

        moments = _clutch_moments(df_p)

        if moments.empty:
            st.info("No clutch moments found with the current filters.")
        else:
            for i, r in enumerate(moments.itertuples(), 1):
                # Gold / Silver / Bronze for top 3
                if i == 1:
                    border_col = "#FFD700"
                    rank_bg = "#FFD700"
                elif i == 2:
                    border_col = "#C0C0C0"
                    rank_bg = "#C0C0C0"
                elif i == 3:
                    border_col = "#CD7F32"
                    rank_bg = "#CD7F32"
                else:
                    border_col = ACCENT3
                    rank_bg = "rgba(255,255,255,0.08)"

                t_color = TEAM_COLORS.get(r.batting_team, ACCENT)

                st.markdown(f"""
<div class='moment-card' style='border-left-color:{border_col};'>
<div style='display:flex;align-items:center;gap:14px;'>
<span class='rank-badge' style='background:{rank_bg};
color:{"#000" if i <= 3 else TEXT_COLOR};font-size:14px;'>
{i}
</span>
<div style='flex:1;'>
<div style='font-weight:700;font-size:16px;color:white;'>
{r.batter}
<span style='color:{t_color};font-size:12px;margin-left:8px;'>
{r.batting_team}
</span>
</div>
<div style='color:rgba(255,255,255,0.5);font-size:12px;margin-top:2px;'>
vs {r.bowling_team} · Season {r.season}
</div>
</div>
<div style='text-align:right;'>
<div style='font-size:24px;font-weight:700;color:{ACCENT3};'>
{r.hp_runs}*
</div>
<div style='color:rgba(255,255,255,0.4);font-size:11px;'>
off {r.hp_balls} HP balls
</div>
</div>
<div style='text-align:center;padding:0 10px;'>
<div style='font-size:16px;font-weight:600;color:{ACCENT};'>{r.hp_sr}</div>
<div style='color:rgba(255,255,255,0.4);font-size:10px;'>SR</div>
</div>
<div style='text-align:center;'>
<div style='font-size:13px;color:{ACCENT2};'>
{r.hp_fours}×4 &nbsp; {r.hp_sixes}×6
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div style='color:rgba(255,255,255,0.3);font-size:11px;margin-top:8px;'>
* Runs scored only on high-pressure deliveries (pressure ≥ 60) in that match.
</div>
""", unsafe_allow_html=True)

    # ================================================================
    # TAB 4 — PRESSURE VS PERFORMANCE SCATTER
    # ================================================================
    with tab4:
        st.markdown("""
<div style='color:rgba(255,255,255,0.5);font-size:13px;margin-bottom:16px;'>
Each bubble is a batter. X-axis = average pressure they face, Y-axis = their
strike rate under high pressure. Bubble size = total balls faced. Top-right
quadrant = true clutch performers.
</div>
""", unsafe_allow_html=True)

        scat = _scatter_data(df_p)

        if scat.empty:
            st.info("Not enough data for the scatter plot.")
        else:
            # Compute medians for quadrant lines
            med_pressure = scat["avg_pressure"].median()
            med_sr = scat["hp_sr"].median()

            colors = [TEAM_COLORS.get(t, ACCENT) for t in scat["team"]]

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=scat["avg_pressure"],
                y=scat["hp_sr"],
                mode="markers",
                marker=dict(
                    size=np.clip(scat["total_balls"] / 40, 6, 35),
                    color=colors,
                    line=dict(width=1, color="rgba(255,255,255,0.2)"),
                    opacity=0.85,
                ),
                text=scat["batter"],
                customdata=np.stack([
                    scat["team"], scat["total_balls"], scat["hp_balls"], scat["hp_sr"]
                ], axis=-1),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Team: %{customdata[0]}<br>"
                    "Avg Pressure: %{x:.1f}<br>"
                    "HP Strike Rate: %{y:.1f}<br>"
                    "Total Balls: %{customdata[1]}<br>"
                    "HP Balls: %{customdata[2]}<extra></extra>"
                ),
            ))

            # Quadrant lines
            fig.add_hline(y=med_sr, line_dash="dot", line_color="rgba(255,255,255,0.15)",
                          annotation_text=f"Median HP SR: {med_sr:.0f}",
                          annotation_font_color="rgba(255,255,255,0.3)")
            fig.add_vline(x=med_pressure, line_dash="dot", line_color="rgba(255,255,255,0.15)",
                          annotation_text=f"Median Pressure: {med_pressure:.0f}",
                          annotation_font_color="rgba(255,255,255,0.3)")

            # Quadrant labels
            x_range = scat["avg_pressure"].max() - scat["avg_pressure"].min()
            y_range = scat["hp_sr"].max() - scat["hp_sr"].min()

            annotations = [
                dict(
                    x=med_pressure + x_range * 0.25,
                    y=med_sr + y_range * 0.4,
                    text="⚡ Clutch Performers",
                    showarrow=False,
                    font=dict(color=ACCENT, size=13, family="Arial Black"),
                    opacity=0.6,
                ),
                dict(
                    x=med_pressure + x_range * 0.25,
                    y=med_sr - y_range * 0.35,
                    text="📉 Crumbles Under Pressure",
                    showarrow=False,
                    font=dict(color=ACCENT3, size=12, family="Arial Black"),
                    opacity=0.5,
                ),
                dict(
                    x=med_pressure - x_range * 0.25,
                    y=med_sr + y_range * 0.4,
                    text="🛡️ Low-Pressure Hitters",
                    showarrow=False,
                    font=dict(color=ACCENT2, size=12, family="Arial Black"),
                    opacity=0.5,
                ),
                dict(
                    x=med_pressure - x_range * 0.25,
                    y=med_sr - y_range * 0.35,
                    text="🐢 Quiet Performers",
                    showarrow=False,
                    font=dict(color="rgba(255,255,255,0.3)", size=11, family="Arial Black"),
                    opacity=0.4,
                ),
            ]

            _plotly_dark_layout(fig,
                title="Pressure vs Performance — Who Thrives Under Heat?",
                xaxis_title="Average Pressure Faced",
                yaxis_title="Strike Rate Under High Pressure (≥60)",
                height=560,
            )
            fig.update_layout(
                annotations=annotations,
                showlegend=False,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Quick insight
            if not scat.empty:
                top_clutch = scat[
                    (scat["avg_pressure"] >= med_pressure) & (scat["hp_sr"] >= med_sr)
                ].sort_values("hp_sr", ascending=False).head(5)

                if not top_clutch.empty:
                    names = ", ".join(top_clutch["batter"].tolist())
                    st.markdown(_glass_card(f"""
<div style='font-size:13px;'>
<span style='color:{ACCENT};font-weight:700;'>⚡ Top Clutch Performers:</span>
<span style='color:rgba(255,255,255,0.7);'> {names}</span>
<br><span style='color:rgba(255,255,255,0.4);font-size:11px;'>
These batters face above-average pressure AND maintain elite strike rates.</span>
</div>
""", border_color=ACCENT), unsafe_allow_html=True)
