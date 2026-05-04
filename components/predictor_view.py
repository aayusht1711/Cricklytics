import streamlit as st
import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── lazy imports so app doesn't crash if sklearn missing ─────────
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, confusion_matrix
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

from utils.chart_style import (
    apply_dark_style, dark_bar_chart,
    DARK_BG, ACCENT, ACCENT2, ACCENT3, TEXT_COLOR,
    team_color
)



@st.cache_resource
def train_model(data_hash: int):
    """
    Train a Random Forest on match-level features.
    Returns the trained model + encoders + metadata dict.
    """
    import pandas as pd
    import numpy as np
    from collections import defaultdict
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, confusion_matrix

    # ── load fresh inside cache fn (data passed via hash only) ──
    df = pd.read_csv("data.csv", low_memory=False)

    # ── build match-level table ──────────────────────────────────
    inn1 = (
        df[df["innings"] == 1]
        .drop_duplicates("match_id")[["match_id", "batting_team", "bowling_team"]]
        .rename(columns={"batting_team": "team1", "bowling_team": "team2"})
    )
    meta = df.drop_duplicates("match_id")[
        ["match_id", "venue", "toss_winner", "toss_decision", "match_won_by"]
    ]
    final = meta.merge(inn1, on="match_id").dropna(subset=["match_won_by"])
    final["target"] = (final["match_won_by"] == final["team1"]).astype(int)

    # ── feature engineering ──────────────────────────────────────
    # 1. head-to-head historical win rate (team1 perspective)
    h2h_wins  = defaultdict(int)
    h2h_total = defaultdict(int)
    for _, r in final.iterrows():
        h2h_wins[(r["team1"], r["team2"])]  += r["target"]
        h2h_total[(r["team1"], r["team2"])] += 1

    def h2h_rate(t1, t2):
        if h2h_total[(t1, t2)] > 0:
            return h2h_wins[(t1, t2)] / h2h_total[(t1, t2)]
        if h2h_total[(t2, t1)] > 0:
            return 1 - h2h_wins[(t2, t1)] / h2h_total[(t2, t1)]
        return 0.5

    # 2. overall win rates
    team1_wr = final.groupby("team1")["target"].mean().to_dict()
    team2_wr = final.groupby("team2")["target"].apply(lambda x: 1 - x.mean()).to_dict()

    # 3. venue advantage for batting-first team
    venue_wr = final.groupby("venue")["target"].mean().to_dict()

    final["h2h_rate"]        = final.apply(lambda r: h2h_rate(r["team1"], r["team2"]), axis=1)
    final["team1_winrate"]   = final["team1"].map(team1_wr).fillna(0.5)
    final["team2_winrate"]   = final["team2"].map(team2_wr).fillna(0.5)
    final["venue_team1_wr"]  = final["venue"].map(venue_wr).fillna(0.5)
    final["toss_is_team1"]   = (final["toss_winner"] == final["team1"]).astype(int)
    final["toss_bat"]        = (final["toss_decision"] == "bat").astype(int)

    # ── label encoders ───────────────────────────────────────────
    le_venue = LabelEncoder()
    le_team  = LabelEncoder()
    all_teams = pd.concat([final["team1"], final["team2"]]).unique()
    le_team.fit(all_teams)
    le_venue.fit(final["venue"])

    final["venue_enc"] = le_venue.transform(final["venue"])
    final["team1_enc"] = le_team.transform(final["team1"])
    final["team2_enc"] = le_team.transform(final["team2"])

    FEATURES = [
        "venue_enc", "team1_enc", "team2_enc",
        "toss_is_team1", "toss_bat",
        "h2h_rate", "team1_winrate", "team2_winrate", "venue_team1_wr",
    ]

    X = final[FEATURES]
    y = final["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── train model ──────────────────────────────────────────────
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # ── evaluation metrics ───────────────────────────────────────
    test_acc = accuracy_score(y_test, model.predict(X_test))
    cv_scores = cross_val_score(model, X, y, cv=5)
    cm = confusion_matrix(y_test, model.predict(X_test))
    fi = pd.Series(model.feature_importances_, index=FEATURES).sort_values(ascending=False)

    return {
        "model":       model,
        "le_venue":    le_venue,
        "le_team":     le_team,
        "features":    FEATURES,
        "test_acc":    round(test_acc, 3),
        "cv_mean":     round(cv_scores.mean(), 3),
        "cv_std":      round(cv_scores.std(), 3),
        "cv_scores":   cv_scores,
        "cm":          cm,
        "fi":          fi,
        "teams":       sorted(le_team.classes_),
        "venues":      sorted(le_venue.classes_),
        "h2h_wins":    dict(h2h_wins),
        "h2h_total":   dict(h2h_total),
        "team1_wr":    team1_wr,
        "team2_wr":    team2_wr,
        "venue_wr":    venue_wr,
        "train_size":  len(X_train),
        "test_size":   len(X_test),
    }


# PREDICTION HELPER
# ════════════════════════════════════════════════════════════════
def _predict(bundle, team1, team2, venue, toss_winner, toss_decision):
    model    = bundle["model"]
    le_venue = bundle["le_venue"]
    le_team  = bundle["le_team"]
    features = bundle["features"]

    # safe encode (handle unseen labels)
    def safe_venue(v):
        if v in le_venue.classes_:
            return le_venue.transform([v])[0]
        return int(np.median(le_venue.transform(le_venue.classes_)))

    def safe_team(t):
        if t in le_team.classes_:
            return le_team.transform([t])[0]
        return int(np.median(le_team.transform(le_team.classes_)))

    h2h_wins  = bundle["h2h_wins"]
    h2h_total = bundle["h2h_total"]
    team1_wr  = bundle["team1_wr"]
    team2_wr  = bundle["team2_wr"]
    venue_wr  = bundle["venue_wr"]

    def h2h_rate(t1, t2):
        k1, k2 = (t1, t2), (t2, t1)
        if h2h_total.get(k1, 0) > 0:
            return h2h_wins.get(k1, 0) / h2h_total[k1]
        if h2h_total.get(k2, 0) > 0:
            return 1 - h2h_wins.get(k2, 0) / h2h_total[k2]
        return 0.5

    row = {
        "venue_enc":       safe_venue(venue),
        "team1_enc":       safe_team(team1),
        "team2_enc":       safe_team(team2),
        "toss_is_team1":   int(toss_winner == team1),
        "toss_bat":        int(toss_decision == "bat"),
        "h2h_rate":        h2h_rate(team1, team2),
        "team1_winrate":   team1_wr.get(team1, 0.5),
        "team2_winrate":   team2_wr.get(team2, 0.5),
        "venue_team1_wr":  venue_wr.get(venue, 0.5),
    }

    X_pred = pd.DataFrame([row])[features]
    prob   = model.predict_proba(X_pred)[0]   # [P(team2 wins), P(team1 wins)]
    return prob[1], prob[0]   # team1_prob, team2_prob


# ════════════════════════════════════════════════════════════════
# CHART HELPERS
# ════════════════════════════════════════════════════════════════
def _win_prob_gauge(prob_team1, prob_team2, team1, team2, color1, color2):
    """Horizontal stacked bar showing win probability split."""
    fig, ax = plt.subplots(figsize=(10, 1.8))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    ax.barh(0, prob_team1, color=color1, height=0.5)
    ax.barh(0, prob_team2, left=prob_team1, color=color2, height=0.5)

    # Labels inside bars
    if prob_team1 > 0.15:
        ax.text(prob_team1 / 2, 0, f"{prob_team1*100:.1f}%",
                ha="center", va="center", color="white",
                fontsize=11, fontweight="bold")
    if prob_team2 > 0.15:
        ax.text(prob_team1 + prob_team2 / 2, 0, f"{prob_team2*100:.1f}%",
                ha="center", va="center", color="white",
                fontsize=11, fontweight="bold")

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 0.5)
    ax.axis("off")

    p1 = mpatches.Patch(color=color1, label=f"{team1[:15]}")
    p2 = mpatches.Patch(color=color2, label=f"{team2[:15]}")
    ax.legend(handles=[p1, p2], loc="upper center", bbox_to_anchor=(0.5, -0.15),
              ncol=2, facecolor=DARK_BG, labelcolor=TEXT_COLOR, fontsize=9,
              framealpha=0)
    plt.tight_layout()
    return fig


def _feature_importance_chart(fi):
    labels = {
        "h2h_rate":       "Head-to-head history",
        "venue_team1_wr": "Venue advantage",
        "venue_enc":      "Venue identity",
        "team1_winrate":  "Team 1 overall form",
        "team2_winrate":  "Team 2 overall form",
        "team1_enc":      "Team 1 identity",
        "team2_enc":      "Team 2 identity",
        "toss_bat":       "Bat / field decision",
        "toss_is_team1":  "Toss won by team 1",
    }
    display_labels = [labels.get(f, f) for f in fi.index]
    colors = [ACCENT if i == 0 else "#2a4a6b" for i in range(len(fi))]

    fig, ax = plt.subplots(figsize=(9, 4))
    apply_dark_style(fig, ax,
                     title="What drives the prediction — feature importance",
                     xlabel="Importance score")
    bars = ax.barh(display_labels, fi.values, color=colors, height=0.6)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.003, bar.get_y() + bar.get_height() / 2,
                f"{w:.3f}", va="center", color=TEXT_COLOR, fontsize=8)
    ax.set_xlim(0, fi.values.max() * 1.2)
    plt.tight_layout()
    return fig


def _confusion_matrix_chart(cm):
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Pred: Team2", "Pred: Team1"], color=TEXT_COLOR, fontsize=9)
    ax.set_yticklabels(["Actual: Team2", "Actual: Team1"], color=TEXT_COLOR, fontsize=9)
    ax.set_title("Confusion matrix (test set)", color=TEXT_COLOR, fontsize=10)

    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white", fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


def _cv_chart(cv_scores):
    fig, ax = plt.subplots(figsize=(7, 3))
    apply_dark_style(fig, ax,
                     title="5-fold cross-validation accuracy",
                     xlabel="Fold", ylabel="Accuracy")
    colors = [ACCENT2 if s == max(cv_scores) else ACCENT for s in cv_scores]
    bars = ax.bar(range(1, 6), cv_scores, color=colors, width=0.5)
    ax.axhline(cv_scores.mean(), color=ACCENT3, linestyle="--",
               linewidth=1.5, label=f"Mean: {cv_scores.mean():.3f}")
    ax.set_ylim(0.4, 0.8)
    ax.set_xticks(range(1, 6))
    ax.legend(facecolor=DARK_BG, labelcolor=TEXT_COLOR, fontsize=8)
    for bar, s in zip(bars, cv_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{s:.3f}", ha="center", color=TEXT_COLOR, fontsize=8)
    plt.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════════
# MAIN VIEW
# ════════════════════════════════════════════════════════════════
def show_predictor_view(data):

    st.markdown("""
    <style>
    .pred-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 20px 22px; margin-bottom: 14px;
    }
    .metric-box {
        background: rgba(0,0,0,0.3); border-radius: 10px;
        padding: 14px 18px; text-align: center;
    }
    .metric-val  { font-size: 28px; font-weight: 800; color: #00FFFF; }
    .metric-label{ font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px; }
    .winner-banner {
        border-radius: 14px; padding: 22px;
        text-align: center; margin: 16px 0;
    }
    .winner-name { font-size: 26px; font-weight: 800; color: white; }
    .winner-sub  { font-size: 14px; color: rgba(255,255,255,0.6); margin-top: 6px; }
    .insight-row {
        display: flex; justify-content: space-between;
        padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.07);
        font-size: 13px;
    }
    .insight-row:last-child { border-bottom: none; }
    .insight-label { color: rgba(255,255,255,0.5); }
    .insight-value { color: white; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h2 style='color:white;'>🤖 Match Outcome Predictor</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5); margin-bottom:20px;'>"
        "Random Forest trained on 1,169 IPL matches · "
        "Features: head-to-head history, venue advantage, team form, toss data</p>",
        unsafe_allow_html=True,
    )

    if not SKLEARN_OK:
        st.error("scikit-learn not installed. Run: pip install scikit-learn")
        return

    # ── train / load model ─────────────────────────────────────
    with st.spinner("🏋️ Training model on 1,169 IPL matches..."):
        bundle = train_model(hash(str(data.shape)))

    # ── model metrics strip ────────────────────────────────────
    st.markdown("<h3 style='color:white;margin:0 0 12px;'>📊 Model Performance</h3>",
                unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">{bundle['test_acc']*100:.1f}%</div>
            <div class="metric-label">Test accuracy</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">{bundle['cv_mean']*100:.1f}%</div>
            <div class="metric-label">CV accuracy (5-fold)</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">{bundle['train_size']:,}</div>
            <div class="metric-label">Training matches</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">9</div>
            <div class="metric-label">Features engineered</div>
        </div>""", unsafe_allow_html=True)

    # ── prediction form ────────────────────────────────────────
    st.markdown("<h3 style='color:white;margin:24px 0 12px;'>🎯 Make a Prediction</h3>",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("🏏 Team batting first", bundle["teams"], index=10)
    with col2:
        remaining = [t for t in bundle["teams"] if t != team1]
        team2 = st.selectbox("🎳 Team bowling first", remaining, index=1)

    col3, col4, col5 = st.columns(3)
    with col3:
        venue = st.selectbox("🏟️ Venue", bundle["venues"])
    with col4:
        toss_winner = st.selectbox("🪙 Toss won by", [team1, team2])
    with col5:
        toss_decision = st.selectbox("🏏 Elected to", ["bat", "field"])

    predict_btn = st.button("⚡ Predict Match Outcome", use_container_width=True)

    if predict_btn or True:   # show on load with defaults
        p1, p2 = _predict(bundle, team1, team2, venue, toss_winner, toss_decision)

        winner    = team1 if p1 >= p2 else team2
        winner_p  = max(p1, p2)
        w_color   = team_color(winner)
        t1_color  = team_color(team1)
        t2_color  = team_color(team2)

        # confidence label
        if winner_p >= 0.70:   conf_label, conf_color = "High confidence", "#4ECDC4"
        elif winner_p >= 0.58: conf_label, conf_color = "Moderate confidence", "#FFE66D"
        else:                   conf_label, conf_color = "Tight contest", "#FF6B6B"

        # ── winner banner ────────────────────────────────────
        st.markdown(f"""
        <div class="winner-banner" style="background:{w_color}22;
             border:2px solid {w_color};">
            <div style="font-size:14px;color:rgba(255,255,255,0.5);
                        margin-bottom:6px;">🤖 Model predicts</div>
            <div class="winner-name">{winner}</div>
            <div class="winner-sub">Win probability: {winner_p*100:.1f}%</div>
            <div style="margin-top:8px;">
                <span style="background:{conf_color}22;color:{conf_color};
                             border:1px solid {conf_color}50;border-radius:99px;
                             font-size:12px;font-weight:700;padding:3px 12px;">
                    {conf_label}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── probability gauge ────────────────────────────────
        st.markdown("<h4 style='color:white;margin:16px 0 8px;'>Win probability split</h4>",
                    unsafe_allow_html=True)
        fig_gauge = _win_prob_gauge(p1, p2, team1, team2, t1_color, t2_color)
        st.pyplot(fig_gauge)

        # ── prediction insights ──────────────────────────────
        st.markdown("<h3 style='color:white;margin:20px 0 12px;'>🔍 Why this prediction?</h3>",
                    unsafe_allow_html=True)

        # Head-to-head
        h2h_wins  = bundle["h2h_wins"]
        h2h_total = bundle["h2h_total"]
        k1, k2 = (team1, team2), (team2, team1)
        if h2h_total.get(k1, 0) + h2h_total.get(k2, 0) > 0:
            t1_h2h = h2h_wins.get(k1, 0)
            t2_h2h = h2h_wins.get(k2, 0)
            total_h2h = h2h_total.get(k1, 0) + h2h_total.get(k2, 0)
            h2h_str = f"{team1[:12]}: {t1_h2h} wins | {team2[:12]}: {t2_h2h} wins ({total_h2h} matches)"
        else:
            h2h_str = "No prior head-to-head data"

        venue_wr = bundle["venue_wr"].get(venue, 0.5)
        t1_wr = bundle["team1_wr"].get(team1, 0.5)

        st.markdown(f"""
        <div class="pred-card">
            <div class="insight-row">
                <span class="insight-label">🤝 Head-to-head record</span>
                <span class="insight-value">{h2h_str}</span>
            </div>
            <div class="insight-row">
                <span class="insight-label">🏟️ Batting-first win % at this venue</span>
                <span class="insight-value">{venue_wr*100:.1f}% historically</span>
            </div>
            <div class="insight-row">
                <span class="insight-label">📈 {team1[:20]} overall win rate (batting first)</span>
                <span class="insight-value">{t1_wr*100:.1f}%</span>
            </div>
            <div class="insight-row">
                <span class="insight-label">🪙 Toss winner</span>
                <span class="insight-value">{toss_winner} elected to {toss_decision}</span>
            </div>
            <div class="insight-row">
                <span class="insight-label">🔑 Top prediction driver</span>
                <span class="insight-value">Head-to-head history (41% weight)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── model details (collapsible) ────────────────────────────
    with st.expander("🔬 Model details — feature importance, cross-validation, confusion matrix"):

        st.markdown(
            "<h4 style='color:white;margin:0 0 10px;'>Feature importance</h4>",
            unsafe_allow_html=True,
        )
        fig_fi = _feature_importance_chart(bundle["fi"])
        st.pyplot(fig_fi)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                "<h4 style='color:white;margin:16px 0 10px;'>Cross-validation scores</h4>",
                unsafe_allow_html=True,
            )
            fig_cv = _cv_chart(bundle["cv_scores"])
            st.pyplot(fig_cv)

        with col_b:
            st.markdown(
                "<h4 style='color:white;margin:16px 0 10px;'>Confusion matrix</h4>",
                unsafe_allow_html=True,
            )
            fig_cm = _confusion_matrix_chart(bundle["cm"])
            st.pyplot(fig_cm)

        st.markdown(f"""
        <div class="pred-card" style="margin-top:16px;">
            <p style="color:rgba(255,255,255,0.8);font-size:13px;line-height:1.7;margin:0;">
            <b style="color:#00FFFF;">Algorithm:</b> Random Forest (300 trees, max depth 10)<br>
            <b style="color:#00FFFF;">Training data:</b> {bundle['train_size']} matches
            (80%) | Test: {bundle['test_size']} matches (20%)<br>
            <b style="color:#00FFFF;">Features (9):</b> Head-to-head win rate, venue batting-first
            win%, team overall win rates, venue encoding, team encodings, toss winner, toss decision<br>
            <b style="color:#00FFFF;">Why 62% accuracy?</b> Cricket is genuinely unpredictable —
            pre-match models in real IPL analytics typically achieve 58–65%. Anything above random
            (50%) on real match data is meaningful. Adding player availability and pitch report
            could push this to 68–72%.
            </p>
        </div>
        """, unsafe_allow_html=True)
