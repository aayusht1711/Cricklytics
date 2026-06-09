import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

TEAM_COLORS = {
    "Mumbai Indians": "#005DA0", "Chennai Super Kings": "#F7C010",
    "Royal Challengers Bangalore": "#EC1C24", "Royal Challengers Bengaluru": "#EC1C24",
    "Kolkata Knight Riders": "#3A225D", "Rajasthan Royals": "#EA1A85",
    "Sunrisers Hyderabad": "#F7700E", "Delhi Daredevils": "#0078BC",
    "Delhi Capitals": "#0078BC", "Kings XI Punjab": "#DCDDDF",
    "Punjab Kings": "#ED1B24", "Deccan Chargers": "#FDB933",
    "Gujarat Titans": "#1C4966", "Lucknow Super Giants": "#A72056",
}


@st.cache_resource
def _get_model(shape):
    """Train the same RF model used in predictor_view."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        import pandas as pd
        from collections import defaultdict

        df = pd.read_csv("data.csv", low_memory=False)

        inn1 = (
            df[df["innings"] == 1]
            .drop_duplicates("match_id")[["match_id", "batting_team", "bowling_team"]]
            .rename(columns={"batting_team": "team1", "bowling_team": "team2"})
        )
        meta  = df.drop_duplicates("match_id")[
            ["match_id", "venue", "toss_winner", "toss_decision", "match_won_by"]
        ]
        final = meta.merge(inn1, on="match_id").dropna(subset=["match_won_by"])
        final["target"] = (final["match_won_by"] == final["team1"]).astype(int)

        h2h_wins  = defaultdict(int)
        h2h_total = defaultdict(int)
        for _, r in final.iterrows():
            h2h_wins[(r["team1"], r["team2"])]  += r["target"]
            h2h_total[(r["team1"], r["team2"])] += 1

        team1_wr = final.groupby("team1")["target"].mean().to_dict()
        team2_wr = final.groupby("team2")["target"].apply(lambda x: 1 - x.mean()).to_dict()
        venue_wr = final.groupby("venue")["target"].mean().to_dict()

        def h2h_rate(t1, t2):
            if h2h_total[(t1, t2)] > 0: return h2h_wins[(t1, t2)] / h2h_total[(t1, t2)]
            if h2h_total[(t2, t1)] > 0: return 1 - h2h_wins[(t2, t1)] / h2h_total[(t2, t1)]
            return 0.5

        final["h2h_rate"]       = final.apply(lambda r: h2h_rate(r["team1"], r["team2"]), axis=1)
        final["team1_winrate"]  = final["team1"].map(team1_wr).fillna(0.5)
        final["team2_winrate"]  = final["team2"].map(team2_wr).fillna(0.5)
        final["venue_team1_wr"] = final["venue"].map(venue_wr).fillna(0.5)
        final["toss_is_team1"]  = (final["toss_winner"] == final["team1"]).astype(int)
        final["toss_bat"]       = (final["toss_decision"] == "bat").astype(int)

        le_venue = LabelEncoder(); le_team = LabelEncoder()
        all_teams = pd.concat([final["team1"], final["team2"]]).unique()
        le_team.fit(all_teams); le_venue.fit(final["venue"])
        final["venue_enc"] = le_venue.transform(final["venue"])
        final["team1_enc"] = le_team.transform(final["team1"])
        final["team2_enc"] = le_team.transform(final["team2"])

        FEATURES = ["venue_enc","team1_enc","team2_enc","toss_is_team1","toss_bat",
                    "h2h_rate","team1_winrate","team2_winrate","venue_team1_wr"]

        model = RandomForestClassifier(n_estimators=200, max_depth=10,
                                       min_samples_leaf=5, random_state=42)
        model.fit(final[FEATURES], final["target"])

        return {"model": model, "le_venue": le_venue, "le_team": le_team,
                "FEATURES": FEATURES, "h2h_wins": dict(h2h_wins),
                "h2h_total": dict(h2h_total), "team1_wr": team1_wr,
                "team2_wr": team2_wr, "venue_wr": venue_wr,
                "teams": sorted(le_team.classes_), "venues": sorted(le_venue.classes_)}
    except Exception as e:
        return None


def _predict_prob(bundle, team1, team2, venue, toss_winner, toss_decision):
    import numpy as np
    model    = bundle["model"]
    le_venue = bundle["le_venue"]
    le_team  = bundle["le_team"]
    FEATURES = bundle["FEATURES"]

    def safe_v(v): return le_venue.transform([v])[0] if v in le_venue.classes_ else 0
    def safe_t(t): return le_team.transform([t])[0]  if t in le_team.classes_  else 0

    h2h_wins  = bundle["h2h_wins"]
    h2h_total = bundle["h2h_total"]
    def h2h(t1, t2):
        if h2h_total.get((t1,t2), 0) > 0: return h2h_wins.get((t1,t2),0)/h2h_total[(t1,t2)]
        if h2h_total.get((t2,t1), 0) > 0: return 1 - h2h_wins.get((t2,t1),0)/h2h_total[(t2,t1)]
        return 0.5

    row = {
        "venue_enc":      safe_v(venue),
        "team1_enc":      safe_t(team1),
        "team2_enc":      safe_t(team2),
        "toss_is_team1":  int(toss_winner == team1),
        "toss_bat":       int(toss_decision == "bat"),
        "h2h_rate":       h2h(team1, team2),
        "team1_winrate":  bundle["team1_wr"].get(team1, 0.5),
        "team2_winrate":  bundle["team2_wr"].get(team2, 0.5),
        "venue_team1_wr": bundle["venue_wr"].get(venue, 0.5),
    }
    import pandas as pd
    X = pd.DataFrame([row])[FEATURES]
    prob = model.predict_proba(X)[0]
    return round(prob[1] * 100, 1), round(prob[0] * 100, 1)


@st.cache_data
def _get_match_list(data):
    m = data.drop_duplicates("match_id")[[
        "match_id", "date", "season", "batting_team", "bowling_team",
        "venue", "toss_winner", "toss_decision", "match_won_by",
        "win_outcome", "player_of_match"
    ]].dropna(subset=["match_won_by"]).copy()
    m["label"] = (
        m["season"].astype(str) + " | " +
        m["batting_team"].str[:12] + " vs " +
        m["bowling_team"].str[:12] + " (" +
        m["match_won_by"].str[:10] + " won)"
    )
    return m.sort_values("date", ascending=False).reset_index(drop=True)


def _gauge_chart(original, whatif, team1, team2):
    fig, axes = plt.subplots(1, 2, figsize=(10, 2))
    fig.patch.set_facecolor("#0e1117")

    for ax, (p1, p2), title in zip(
        axes,
        [(original[0]/100, original[1]/100), (whatif[0]/100, whatif[1]/100)],
        ["Original Match", "What If Scenario"],
    ):
        ax.set_facecolor("#0e1117")
        c1 = TEAM_COLORS.get(team1, "#00FFFF")
        c2 = TEAM_COLORS.get(team2, "#FF6B6B")
        ax.barh(0, p1, color=c1, height=0.4)
        ax.barh(0, p2, left=p1, color=c2, height=0.4)
        if p1 > 0.15:
            ax.text(p1/2, 0, f"{p1*100:.0f}%", ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")
        if p2 > 0.15:
            ax.text(p1 + p2/2, 0, f"{p2*100:.0f}%", ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")
        ax.set_xlim(0, 1); ax.set_ylim(-0.5, 0.5)
        ax.axis("off")
        ax.set_title(title, color="white", fontsize=10)

    plt.tight_layout()
    return fig


def show_whatif_view(data):
    st.markdown("<h2>What If Simulator</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5);margin-bottom:20px;'>"
        "Pick any IPL match, change one variable — see how win probability shifts</p>",
        unsafe_allow_html=True,
    )

    try:
        from sklearn.ensemble import RandomForestClassifier
        SKLEARN_OK = True
    except ImportError:
        SKLEARN_OK = False
        st.error("Run: pip install scikit-learn")
        return

    with st.spinner("Loading ML model..."):
        bundle = _get_model(str(data.shape))

    if bundle is None:
        st.error("Could not train model. Make sure data.csv is in your project root.")
        return

    match_list = _get_match_list(data)

    # Match selector
    st.markdown("<h3>Step 1 — Pick a Match</h3>", unsafe_allow_html=True)
    col_s, col_f = st.columns([3, 1])
    with col_f:
        season_opts = ["All"] + sorted(data["season"].astype(str).unique().tolist(), reverse=True)
        sel_season  = st.selectbox("Season", season_opts)
    with col_s:
        filtered = match_list if sel_season == "All" else \
                   match_list[match_list["season"].astype(str) == sel_season]
        chosen_label = st.selectbox("Choose match", filtered["label"].tolist())

    row     = filtered[filtered["label"] == chosen_label].iloc[0]
    team1   = row["batting_team"]
    team2   = row["bowling_team"]
    venue   = row["venue"]
    toss_w  = row["toss_winner"]
    toss_d  = row["toss_decision"]
    winner  = row["match_won_by"]
    result  = row["win_outcome"]
    pom     = row["player_of_match"]
    mid     = int(row["match_id"])

    t1c = TEAM_COLORS.get(team1, "#00FFFF")
    t2c = TEAM_COLORS.get(team2, "#FF6B6B")

    # Original match card
    st.markdown(
        f"<div class='card'>"
        f"<h3 style='color:{t1c};'>{team1}</h3>"
        f"<p style='color:rgba(255,255,255,0.5);'>vs</p>"
        f"<h3 style='color:{t2c};'>{team2}</h3>"
        f"<p><b>Venue:</b> {venue}</p>"
        f"<p><b>Toss:</b> {toss_w} chose to {toss_d}</p>"
        f"<p><b>Result:</b> {winner} won by {result}</p>"
        f"<p><b>POM:</b> {pom}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Original probability
    orig_p1, orig_p2 = _predict_prob(bundle, team1, team2, venue, toss_w, toss_d)
    st.markdown(
        f"<div class='card'>"
        f"<p><b>Original win probability:</b> &nbsp;"
        f"<span style='color:{t1c};font-weight:800;'>{team1[:15]}: {orig_p1}%</span> &nbsp;|&nbsp; "
        f"<span style='color:{t2c};font-weight:800;'>{team2[:15]}: {orig_p2}%</span></p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("<h3>Step 2 — Change a Variable</h3>", unsafe_allow_html=True)

    scenario = st.selectbox(
        "What do you want to change?",
        [
            "Flip the toss outcome",
            "Change toss decision (bat ↔ field)",
            "Swap the venue",
            "Swap batting and fielding teams",
        ],
    )

    # Build what-if scenario
    wi_team1  = team1
    wi_team2  = team2
    wi_venue  = venue
    wi_toss_w = toss_w
    wi_toss_d = toss_d
    scenario_desc = ""

    if scenario == "Flip the toss outcome":
        wi_toss_w     = team2 if toss_w == team1 else team1
        scenario_desc = f"Toss won by {wi_toss_w} instead of {toss_w}"

    elif scenario == "Change toss decision (bat ↔ field)":
        wi_toss_d     = "field" if toss_d == "bat" else "bat"
        scenario_desc = f"{toss_w} chose to {wi_toss_d} instead of {toss_d}"

    elif scenario == "Swap the venue":
        all_venues = bundle["venues"]
        wi_venue   = st.selectbox("Pick alternative venue", [v for v in all_venues if v != venue])
        scenario_desc = f"Played at {wi_venue} instead of {venue}"

    elif scenario == "Swap batting and fielding teams":
        wi_team1 = team2; wi_team2 = team1
        wi_toss_w = team2 if toss_w == team1 else team1
        scenario_desc = f"{team2} bats first instead of {team1}"

    st.markdown(
        f"<div class='card'>"
        f"<p><b style='color:#FFE66D;'>Scenario:</b> {scenario_desc}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # What-if probability
    wi_p1, wi_p2 = _predict_prob(bundle, wi_team1, wi_team2, wi_venue, wi_toss_w, wi_toss_d)

    delta1 = round(wi_p1 - orig_p1, 1)
    delta2 = round(wi_p2 - orig_p2, 1)
    d1_str = f"+{delta1}" if delta1 >= 0 else str(delta1)
    d2_str = f"+{delta2}" if delta2 >= 0 else str(delta2)

    c1, c2 = st.columns(2)
    c1.metric(f"{team1[:18]} win %", f"{wi_p1}%", d1_str)
    c2.metric(f"{team2[:18]} win %", f"{wi_p2}%", d2_str)

    # Side by side gauge
    fig = _gauge_chart((orig_p1, orig_p2), (wi_p1, wi_p2), team1, team2)
    st.pyplot(fig)

    # Verdict
    orig_fav = team1 if orig_p1 > orig_p2 else team2
    wi_fav   = wi_team1 if wi_p1 > wi_p2 else wi_team2
    change   = abs(delta1)

    if orig_fav != wi_fav:
        verdict = f"This change FLIPS the result — {wi_fav} becomes favourite!"
        v_color = "#FF6B6B"
    elif change >= 10:
        verdict = f"Massive {change}% swing — the variable had huge impact."
        v_color = "#FFE66D"
    elif change >= 5:
        verdict = f"Meaningful {change}% swing — noticeably changes the odds."
        v_color = "#4ECDC4"
    else:
        verdict = f"Small {change}% shift — this variable had limited impact."
        v_color = "rgba(255,255,255,0.6)"

    st.markdown(
        f"<div class='card'>"
        f"<p style='color:{v_color};font-size:16px;font-weight:700;'>Verdict: {verdict}</p>"
        f"<p style='color:rgba(255,255,255,0.5);font-size:13px;margin-top:8px;'>"
        f"Actual result: {winner} won by {result}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<div class='card'>"
        "<p><b style='color:#00FFFF;'>Resume talking point:</b> "
        "Built a counterfactual match simulator using a trained Random Forest model — "
        "users can change toss, venue, or batting order on any of 1,169 IPL matches "
        "and see how win probability shifts in real time.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
