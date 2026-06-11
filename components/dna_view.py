import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.chart_style import TEAM_COLORS, DARK_BG, ACCENT, ACCENT2, ACCENT3, TEXT_COLOR

# ── Constants ────────────────────────────────────────────────────
MIN_BALLS_BAT = 200
MIN_BALLS_BOWL = 100

BATTER_DIMS = ["Power", "Consistency", "Strike Rotation",
                "Death Hitting", "Powerplay Dominance", "Big Innings", "Survival"]
BOWLER_DIMS = ["Wicket Threat", "Economy Control", "Dot Ball %",
               "Death Bowling", "Powerplay Impact", "Spell Consistency", "Boundary Prevention"]


# ── Batter raw stats ────────────────────────────────────────────
@st.cache_data
def _compute_all_batter_stats(data):
    """Compute raw DNA dimensions for every batter with >= MIN_BALLS_BAT."""
    bat = data[data["innings"].isin([1, 2])].copy()
    # per-batter aggregations
    grouped = bat.groupby("batter")
    total_balls = grouped["valid_ball"].sum()
    eligible = total_balls[total_balls >= MIN_BALLS_BAT].index.tolist()
    if not eligible:
        return pd.DataFrame()

    records = []
    for player in eligible:
        pdf = bat[bat["batter"] == player]
        balls = int(pdf["valid_ball"].sum())
        if balls == 0:
            continue
        runs = int(pdf["runs_batter"].sum())
        fours = int((pdf["runs_batter"] == 4).sum())
        sixes = int((pdf["runs_batter"] == 6).sum())
        ones = int((pdf["runs_batter"] == 1).sum())
        twos = int((pdf["runs_batter"] == 2).sum())
        threes = int((pdf["runs_batter"] == 3).sum())

        # Match-level aggregations
        match_runs = pdf.groupby("match_id")["runs_batter"].sum()
        n_innings = len(match_runs)
        dismissals = int(pdf["player_dismissed"].notna().sum()) if "player_dismissed" in pdf.columns else 0

        # Phase data
        death = pdf[pdf["over"] >= 15]
        death_balls = int(death["valid_ball"].sum())
        death_runs = int(death["runs_batter"].sum())

        pp = pdf[pdf["over"] <= 5]
        pp_balls = int(pp["valid_ball"].sum())
        pp_runs = int(pp["runs_batter"].sum())

        # Dimensions
        power = (fours + sixes) / balls * 100
        consistency = runs / n_innings if n_innings > 0 else 0
        rotation = (ones + twos + threes) / balls * 100
        death_sr = (death_runs / death_balls * 100) if death_balls > 0 else 0
        pp_sr = (pp_runs / pp_balls * 100) if pp_balls > 0 else 0
        big_inn_pct = (match_runs >= 50).sum() / n_innings * 100 if n_innings > 0 else 0
        survival = balls / dismissals if dismissals > 0 else balls

        team = pdf["batting_team"].value_counts().index[0] if len(pdf) > 0 else ""

        records.append({
            "player": player,
            "team": team,
            "balls": balls,
            "Power": round(power, 2),
            "Consistency": round(consistency, 2),
            "Strike Rotation": round(rotation, 2),
            "Death Hitting": round(death_sr, 2),
            "Powerplay Dominance": round(pp_sr, 2),
            "Big Innings": round(big_inn_pct, 2),
            "Survival": round(survival, 2),
        })

    df = pd.DataFrame(records)
    return df


@st.cache_data
def _compute_all_bowler_stats(data):
    """Compute raw DNA dimensions for every bowler with >= MIN_BALLS_BOWL."""
    bowl = data[data["innings"].isin([1, 2])].copy()
    grouped = bowl.groupby("bowler")
    total_balls = grouped["valid_ball"].sum()
    eligible = total_balls[total_balls >= MIN_BALLS_BOWL].index.tolist()
    if not eligible:
        return pd.DataFrame()

    records = []
    for player in eligible:
        pdf = bowl[bowl["bowler"] == player]
        balls = int(pdf["valid_ball"].sum())
        if balls == 0:
            continue
        runs_conceded = int(pdf["runs_total"].sum())
        wickets = int(pdf["bowler_wicket"].sum()) if "bowler_wicket" in pdf.columns else 0
        dots = int(((pdf["runs_total"] == 0) & (pdf["valid_ball"] == 1)).sum())

        # Boundaries conceded
        fours_conceded = int((pdf["runs_batter"] == 4).sum())
        sixes_conceded = int((pdf["runs_batter"] == 6).sum())

        n_matches = pdf["match_id"].nunique()

        # Phase data
        death = pdf[pdf["over"] >= 15]
        death_balls = int(death["valid_ball"].sum())
        death_runs = int(death["runs_total"].sum())

        pp = pdf[pdf["over"] <= 5]
        pp_wickets = int(pp["bowler_wicket"].sum()) if "bowler_wicket" in pp.columns else 0

        # Per-match economy for std dev
        match_stats = pdf.groupby("match_id").agg(
            m_runs=("runs_total", "sum"),
            m_balls=("valid_ball", "sum"),
        )
        match_stats["m_econ"] = match_stats["m_runs"] / (match_stats["m_balls"] / 6).replace(0, np.nan)
        econ_std = match_stats["m_econ"].std()
        if pd.isna(econ_std) or econ_std == 0:
            econ_std = 0.01  # avoid div/0

        overall_econ = runs_conceded / (balls / 6) if balls > 0 else 99
        death_econ = death_runs / (death_balls / 6) if death_balls > 0 else 99

        team = pdf["bowling_team"].value_counts().index[0] if "bowling_team" in pdf.columns and len(pdf) > 0 else ""

        records.append({
            "player": player,
            "team": team,
            "balls": balls,
            "Wicket Threat": round(wickets / n_matches, 2) if n_matches > 0 else 0,
            "Economy Control": round(1 / overall_econ * 100, 2) if overall_econ > 0 else 0,
            "Dot Ball %": round(dots / balls * 100, 2) if balls > 0 else 0,
            "Death Bowling": round(1 / death_econ * 100, 2) if death_econ > 0 else 0,
            "Powerplay Impact": round(pp_wickets / n_matches, 2) if n_matches > 0 else 0,
            "Spell Consistency": round(1 / econ_std * 10, 2),
            "Boundary Prevention": round((1 - (fours_conceded + sixes_conceded) / balls) * 100, 2) if balls > 0 else 0,
        })

    df = pd.DataFrame(records)
    return df


@st.cache_data
def _percentile_normalize(df, dims):
    """Convert raw values to percentile ranks (0-100) for each dimension."""
    result = df.copy()
    for dim in dims:
        if dim in result.columns:
            result[dim + "_raw"] = result[dim]
            result[dim] = result[dim].rank(pct=True) * 100
            result[dim] = result[dim].round(1)
    return result


# ── UI Helpers ───────────────────────────────────────────────────
def _inject_css():
    st.markdown("""
    <style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50%      { transform: scale(1.05); }
    }
    .dna-header {
        background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(255,230,109,0.10));
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        border: 1px solid rgba(0,229,255,0.15);
        animation: fadeInUp 0.6s ease-out;
    }
    .dna-header h2 {
        margin: 0; font-size: 32px; color: #ffffff;
        background: linear-gradient(90deg, #00e5ff, #FFE66D);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .dna-header p { color: rgba(255,255,255,0.55); margin: 6px 0 0 0; font-size: 15px; }

    .dna-card {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.06);
        animation: fadeInUp 0.5s ease-out;
    }
    .dna-card-accent {
        border-left: 4px solid var(--accent-color, #00e5ff);
    }
    .dna-card h3 { margin: 0 0 6px 0; font-size: 22px; }
    .dna-card .subtitle { color: rgba(255,255,255,0.55); font-size: 13px; margin: 0; }

    .rating-circle {
        width: 90px; height: 90px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; font-weight: 800; color: #fff;
        position: relative;
        animation: pulse 2s infinite;
    }
    .rating-circle::before {
        content: '';
        position: absolute; inset: 0;
        border-radius: 50%;
        padding: 4px;
        background: conic-gradient(var(--ring-color, #00e5ff) calc(var(--pct, 0) * 3.6deg),
                                    rgba(255,255,255,0.08) 0deg);
        -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 5px), #fff calc(100% - 4px));
        mask: radial-gradient(farthest-side, transparent calc(100% - 5px), #fff calc(100% - 4px));
    }

    .badge-strength {
        display: inline-block; padding: 5px 14px; border-radius: 20px;
        font-size: 12px; font-weight: 700; margin: 3px 4px;
        background: rgba(78,205,196,0.15); color: #4ECDC4;
        border: 1px solid rgba(78,205,196,0.3);
    }
    .badge-weakness {
        display: inline-block; padding: 5px 14px; border-radius: 20px;
        font-size: 12px; font-weight: 700; margin: 3px 4px;
        background: rgba(255,107,107,0.15); color: #FF6B6B;
        border: 1px solid rgba(255,107,107,0.3);
    }

    .stat-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 16px; border-bottom: 1px solid rgba(255,255,255,0.05);
        font-size: 14px;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: rgba(255,255,255,0.6); flex: 1; }
    .stat-val-a { color: #00e5ff; font-weight: 700; text-align: center; flex: 0.6; }
    .stat-val-b { color: #FFE66D; font-weight: 700; text-align: center; flex: 0.6; }
    .stat-bar-wrap { flex: 1.2; display: flex; gap: 4px; align-items: center; }
    .stat-bar {
        height: 6px; border-radius: 3px;
        transition: width 0.8s ease;
    }
    </style>
    """, unsafe_allow_html=True)


def _player_card(name, team, overall, accent_color):
    """Glassmorphism player card with circular rating."""
    r_color = "#4ECDC4" if overall >= 65 else ("#FFE66D" if overall >= 40 else "#FF6B6B")
    st.markdown(f"""
    <div class="dna-card dna-card-accent" style="--accent-color:{accent_color};
         display:flex; align-items:center; gap:24px;">
        <div>
            <div class="rating-circle" style="--pct:{overall}; --ring-color:{r_color};
                 background: rgba(255,255,255,0.06);">
                {int(overall)}
            </div>
            <p style="text-align:center;font-size:11px;color:rgba(255,255,255,0.4);margin:6px 0 0;">
                Overall
            </p>
        </div>
        <div>
            <h3 style="color:{accent_color};">{name}</h3>
            <p class="subtitle">Team: {team}</p>
            <p class="subtitle">DNA Rating: <b style="color:{r_color};">{overall:.1f} / 100</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _strengths_weaknesses(values, dims, label_color_a="#00e5ff"):
    """Auto-detect top 2 and bottom 2 dimensions."""
    paired = list(zip(dims, values))
    paired_sorted = sorted(paired, key=lambda x: x[1], reverse=True)
    strengths = paired_sorted[:2]
    weaknesses = paired_sorted[-2:]

    s_badges = " ".join(
        f'<span class="badge-strength">💪 {d} ({v:.0f})</span>' for d, v in strengths
    )
    w_badges = " ".join(
        f'<span class="badge-weakness">⚠️ {d} ({v:.0f})</span>' for d, v in weaknesses
    )

    st.markdown(f"""
    <div class="dna-card" style="margin-top: 8px;">
        <p style="color:rgba(255,255,255,0.5);font-size:12px;margin:0 0 8px;text-transform:uppercase;
           letter-spacing:1px;">Strengths</p>
        {s_badges}
        <p style="color:rgba(255,255,255,0.5);font-size:12px;margin:14px 0 8px;text-transform:uppercase;
           letter-spacing:1px;">Weaknesses</p>
        {w_badges}
    </div>
    """, unsafe_allow_html=True)


def _comparison_table(dims, vals_a, vals_b, name_a, name_b):
    """Side-by-side comparison bars for each dimension."""
    rows_html = ""
    for dim, va, vb in zip(dims, vals_a, vals_b):
        rows_html += f"""
        <div class="stat-row">
            <span class="stat-val-a">{va:.0f}</span>
            <div class="stat-bar-wrap">
                <div class="stat-bar" style="width:{va}%;background:#00e5ff;"></div>
            </div>
            <span class="stat-label" style="text-align:center;">{dim}</span>
            <div class="stat-bar-wrap" style="justify-content:flex-end;">
                <div class="stat-bar" style="width:{vb}%;background:#FFE66D;"></div>
            </div>
            <span class="stat-val-b">{vb:.0f}</span>
        </div>"""

    st.markdown(f"""
    <div class="dna-card">
        <div class="stat-row" style="border-bottom:2px solid rgba(255,255,255,0.1);padding-bottom:12px;">
            <span class="stat-val-a" style="font-size:15px;">{name_a}</span>
            <span class="stat-label" style="text-align:center;color:rgba(255,255,255,0.35);
                   font-size:12px;text-transform:uppercase;letter-spacing:1px;">Dimension</span>
            <span class="stat-val-b" style="font-size:15px;">{name_b}</span>
        </div>
        {rows_html}
    </div>
    """, unsafe_allow_html=True)


def _single_table(dims, vals, name):
    """Single-player stat table."""
    rows_html = ""
    for dim, v in zip(dims, vals):
        bar_color = "#4ECDC4" if v >= 65 else ("#FFE66D" if v >= 40 else "#FF6B6B")
        rows_html += f"""
        <div class="stat-row">
            <span class="stat-label">{dim}</span>
            <div class="stat-bar-wrap">
                <div class="stat-bar" style="width:{v}%;background:{bar_color};"></div>
            </div>
            <span class="stat-val-a">{v:.0f}</span>
        </div>"""

    st.markdown(f"""
    <div class="dna-card">
        <p style="color:rgba(255,255,255,0.5);font-size:12px;margin:0 0 10px;text-transform:uppercase;
           letter-spacing:1px;">📊 {name} — Dimension Breakdown</p>
        {rows_html}
    </div>
    """, unsafe_allow_html=True)


# ── Radar Chart ──────────────────────────────────────────────────
def _build_radar(categories, values_a, name_a, values_b=None, name_b=None):
    """Build a Plotly polar (spider) chart."""
    fig = go.Figure()

    # Player A
    fig.add_trace(go.Scatterpolar(
        r=values_a + [values_a[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(0,229,255,0.2)',
        line=dict(color='#00e5ff', width=2.5),
        marker=dict(size=6, color='#00e5ff'),
        name=name_a,
    ))

    # Player B (if selected)
    if values_b is not None and name_b:
        fig.add_trace(go.Scatterpolar(
            r=values_b + [values_b[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(255,230,109,0.2)',
            line=dict(color='#FFE66D', width=2.5),
            marker=dict(size=6, color='#FFE66D'),
            name=name_b,
        ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)',
                color='#e0e0e0', tickfont=dict(size=10),
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                color='#e0e0e0',
                tickfont=dict(size=11),
            ),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0', family='DM Sans, sans-serif'),
        showlegend=True,
        legend=dict(
            font=dict(color='#e0e0e0', size=12),
            bgcolor='rgba(0,0,0,0)',
            yanchor='bottom', y=1.02, xanchor='center', x=0.5,
            orientation='h',
        ),
        height=520,
        margin=dict(l=60, r=60, t=40, b=40),
    )
    return fig


# ── Main View ────────────────────────────────────────────────────
def show_dna_view(data):
    _inject_css()

    # ── Header ───────────────────────────────────────────────────
    st.markdown("""
    <div class="dna-header">
        <h2>🧬 Player DNA Radar</h2>
        <p>A unique visual fingerprint for any player — compare batting or bowling DNA side by side</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Controls ─────────────────────────────────────────────────
    col_mode, col_a, col_b = st.columns([1, 1.5, 1.5])

    with col_mode:
        mode = st.selectbox("Mode", ["Batter", "Bowler"], index=0)

    is_batter = mode == "Batter"
    dims = BATTER_DIMS if is_batter else BOWLER_DIMS

    # Compute stats
    if is_batter:
        all_stats = _compute_all_batter_stats(data)
    else:
        all_stats = _compute_all_bowler_stats(data)

    if all_stats.empty:
        st.warning(f"No {mode.lower()}s found with enough data (min "
                   f"{MIN_BALLS_BAT if is_batter else MIN_BALLS_BOWL} balls).")
        return

    # Percentile normalization
    norm_stats = _percentile_normalize(all_stats, dims)
    player_list = sorted(norm_stats["player"].unique().tolist())

    with col_a:
        player_a = st.selectbox("Player A", player_list, index=0)
    with col_b:
        player_b = st.selectbox("Player B (optional)", ["— None —"] + player_list, index=0)
        if player_b == "— None —":
            player_b = None

    # ── Get player rows ──────────────────────────────────────────
    row_a = norm_stats[norm_stats["player"] == player_a]
    if row_a.empty:
        st.error(f"No data found for {player_a}.")
        return
    row_a = row_a.iloc[0]
    vals_a = [float(row_a[d]) for d in dims]
    overall_a = round(np.mean(vals_a), 1)
    team_a = row_a["team"]
    color_a = TEAM_COLORS.get(team_a, ACCENT)

    vals_b = None
    overall_b = None
    team_b = None
    color_b = None
    row_b_data = None
    if player_b:
        row_b = norm_stats[norm_stats["player"] == player_b]
        if not row_b.empty:
            row_b_data = row_b.iloc[0]
            vals_b = [float(row_b_data[d]) for d in dims]
            overall_b = round(np.mean(vals_b), 1)
            team_b = row_b_data["team"]
            color_b = TEAM_COLORS.get(team_b, ACCENT2)

    # ── DNA Cards ────────────────────────────────────────────────
    if player_b and vals_b is not None:
        ca, cb = st.columns(2)
        with ca:
            _player_card(player_a, team_a, overall_a, color_a)
        with cb:
            _player_card(player_b, team_b, overall_b, color_b)
    else:
        _player_card(player_a, team_a, overall_a, color_a)

    # ── Radar Chart ──────────────────────────────────────────────
    fig = _build_radar(
        categories=dims,
        values_a=vals_a,
        name_a=player_a,
        values_b=vals_b,
        name_b=player_b,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Comparison Table / Single Table ──────────────────────────
    st.markdown("""
    <p style="color:rgba(255,255,255,0.4);font-size:12px;text-transform:uppercase;
       letter-spacing:1.5px;margin:10px 0 4px;">📐 Dimension Breakdown</p>
    """, unsafe_allow_html=True)

    if player_b and vals_b is not None:
        _comparison_table(dims, vals_a, vals_b, player_a, player_b)
    else:
        _single_table(dims, vals_a, player_a)

    # ── Strengths & Weaknesses ───────────────────────────────────
    st.markdown("""
    <p style="color:rgba(255,255,255,0.4);font-size:12px;text-transform:uppercase;
       letter-spacing:1.5px;margin:18px 0 4px;">🎯 Strengths & Weaknesses</p>
    """, unsafe_allow_html=True)

    if player_b and vals_b is not None:
        sw_a, sw_b = st.columns(2)
        with sw_a:
            st.markdown(f"<p style='color:#00e5ff;font-weight:700;margin-bottom:2px;'>{player_a}</p>",
                        unsafe_allow_html=True)
            _strengths_weaknesses(vals_a, dims)
        with sw_b:
            st.markdown(f"<p style='color:#FFE66D;font-weight:700;margin-bottom:2px;'>{player_b}</p>",
                        unsafe_allow_html=True)
            _strengths_weaknesses(vals_b, dims)
    else:
        _strengths_weaknesses(vals_a, dims)

    # ── Raw Value Detail (expandable) ────────────────────────────
    with st.expander("📋 Raw Stat Values (before normalization)"):
        raw_cols = [d + "_raw" for d in dims if d + "_raw" in norm_stats.columns]
        if raw_cols:
            show_players = [player_a] + ([player_b] if player_b else [])
            raw_display = norm_stats[norm_stats["player"].isin(show_players)][["player"] + raw_cols].copy()
            raw_display.columns = ["Player"] + dims
            raw_display = raw_display.set_index("Player")
            st.dataframe(raw_display.round(2), use_container_width=True)

    # ── Methodology Note ─────────────────────────────────────────
    st.markdown("""
    <div class="dna-card" style="margin-top:16px;">
        <p style="color:rgba(255,255,255,0.4);font-size:11px;margin:0;">
            <b>📖 Methodology:</b> Each dimension is computed from ball-by-ball data, then
            converted to a <b>percentile rank</b> across all qualified players
            (min """ + str(MIN_BALLS_BAT) + """ balls for batters, """ + str(MIN_BALLS_BOWL) + """ for bowlers).
            A score of 80 means the player is better than 80% of peers in that dimension.
        </p>
    </div>
    """, unsafe_allow_html=True)
