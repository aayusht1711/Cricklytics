import streamlit as st
import pandas as pd
from datetime import datetime
import random

# ── Season award data (precomputed) ─────────────────────────────
SEASON_CHAMPIONS = {
    "2007/08": "Rajasthan Royals",    "2009": "Deccan Chargers",
    "2009/10": "Chennai Super Kings", "2011": "Chennai Super Kings",
    "2012":    "Kolkata Knight Riders","2013": "Mumbai Indians",
    "2014":    "Kolkata Knight Riders","2015": "Mumbai Indians",
    "2016":    "Sunrisers Hyderabad", "2017": "Mumbai Indians",
    "2018":    "Chennai Super Kings", "2019": "Mumbai Indians",
    "2020/21": "Mumbai Indians",      "2021": "Chennai Super Kings",
    "2022":    "Gujarat Titans",      "2023": "Chennai Super Kings",
    "2024":    "Kolkata Knight Riders","2025": "Royal Challengers Bengaluru",
}

ORANGE_CAP = {
    "2007/08":"SE Marsh (616)",    "2009":"ML Hayden (572)",
    "2009/10":"SR Tendulkar (618)","2011":"CH Gayle (608)",
    "2012":   "CH Gayle (733)",    "2013":"MEK Hussey (733)",
    "2014":   "RV Uthappa (660)",  "2015":"DA Warner (562)",
    "2016":   "V Kohli (973)",     "2017":"DA Warner (641)",
    "2018":   "KS Williamson (735)","2019":"DA Warner (692)",
    "2020/21":"KL Rahul (676)",    "2021":"RD Gaikwad (635)",
    "2022":   "JC Buttler (863)",  "2023":"Shubman Gill (890)",
    "2024":   "V Kohli (741)",     "2025":"B Sai Sudharsan (759)",
}

PURPLE_CAP = {
    "2007/08":"Sohail Tanvir (22)", "2009":"RP Singh (23)",
    "2009/10":"PP Ojha (21)",       "2011":"SL Malinga (28)",
    "2012":   "M Morkel (25)",      "2013":"DJ Bravo (32)",
    "2014":   "MM Sharma (23)",     "2015":"DJ Bravo (26)",
    "2016":   "B Kumar (23)",       "2017":"B Kumar (26)",
    "2018":   "AJ Tye (24)",        "2019":"Imran Tahir (26)",
    "2020/21":"K Rabada (32)",      "2021":"HV Patel (32)",
    "2022":   "YS Chahal (27)",     "2023":"Mohammed Shami (28)",
    "2024":   "HV Patel (24)",      "2025":"M Prasidh Krishna (25)",
}

# ── Did You Know facts (static, from your dataset) ───────────────
DID_YOU_KNOW = [
    ("🏏", "CH Gayle holds the IPL record for most sixes — a jaw-dropping 359 maximums across his career."),
    ("⚡", "The highest ever score in a single over in IPL history was 37 runs — an extraordinary assault."),
    ("👑", "AB de Villiers won the Player of the Match award 25 times — more than any other player in IPL history."),
    ("🏆", "Mumbai Indians have played 143 IPL matches — the most of any franchise in the tournament."),
    ("🌟", "V Kohli scored 973 runs in IPL 2016 — the highest ever tally in a single IPL season."),
    ("💣", "Over 14,353 sixes have been hit in IPL history. That's a six roughly every 19 balls."),
    ("🎯", "SP Narine has won Player of the Match 17 times purely as a bowler — a rare feat in T20 cricket."),
    ("📊", "Sunrisers Hyderabad hold the record for the highest team total in IPL — 287 runs in a single innings."),
    ("🔥", "CH Gayle smashed 17 sixes in a single match against KXIP in 2013 — the most ever in one IPL game."),
    ("⭐", "BB McCullum's 158* off 73 balls in the very first IPL match in 2008 set the tone for the tournament."),
    ("🏟️", "IPL matches have been played across 37 cities including Sharjah, Cape Town and Johannesburg."),
    ("💎", "DA Warner won the Orange Cap three times — in 2015, 2017 and 2019."),
]


@st.cache_data(ttl=3600)
def get_today_in_history(data_hash):
    """Find the most dramatic event from today's date in IPL history."""
    import pandas as pd
    # We pass data_hash just for cache keying — actual data comes from session
    return None  # placeholder, actual logic below


def _today_history_events(data):
    """Compute today's historical events from the dataset."""
    today_md = datetime.now().strftime("%m-%d")
    df = data.copy()
    df["_md"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%m-%d")
    today_df = df[df["_md"] == today_md]

    events = []

    if len(today_df) == 0:
        return events

    # Highest individual innings today
    innings = (
        today_df.groupby(["match_id", "batter", "batting_team",
                          "bowling_team", "date"])["runs_batter"]
        .sum().reset_index()
        .sort_values("runs_batter", ascending=False)
    )
    if not innings.empty:
        row = innings.iloc[0]
        yr = str(row["date"])[:4]
        events.append({
            "icon": "🏏",
            "headline": f"{row['batter']} blasted {int(row['runs_batter'])} runs",
            "detail": f"{row['batting_team']} vs {row['bowling_team']} · {yr}",
        })

    # Highest team total today
    team_totals = (
        today_df.groupby(["match_id", "batting_team", "bowling_team", "date"])["runs_total"]
        .sum().reset_index()
        .sort_values("runs_total", ascending=False)
    )
    if not team_totals.empty:
        row = team_totals.iloc[0]
        yr = str(row["date"])[:4]
        events.append({
            "icon": "🔥",
            "headline": f"{row['batting_team']} posted {int(row['runs_total'])} runs",
            "detail": f"vs {row['bowling_team']} · {yr}",
        })

    # Most sixes in a match today
    sixes = (
        today_df[today_df["runs_batter"] == 6]
        .groupby(["match_id", "batter", "date"])
        .size().reset_index(name="sixes")
        .sort_values("sixes", ascending=False)
    )
    if not sixes.empty and sixes.iloc[0]["sixes"] >= 4:
        row = sixes.iloc[0]
        yr = str(row["date"])[:4]
        events.append({
            "icon": "💥",
            "headline": f"{row['batter']} hit {int(row['sixes'])} sixes in one match",
            "detail": f"On this day in {yr}",
        })

    return events[:3]


def show_home(data):
    """Full home page with Today in IPL History, season stats, and Did You Know."""

    # ── inject home styles ───────────────────────────────────────
    st.markdown("""
    <style>
    .home-section-title {
        font-size: 20px; font-weight: 700; color: white;
        margin: 32px 0 14px; letter-spacing: 0.5px;
    }
    .today-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 18px 20px;
        margin-bottom: 12px; transition: 0.2s;
    }
    .today-card:hover { transform: translateY(-3px); }
    .today-icon { font-size: 28px; margin-bottom: 6px; }
    .today-headline { font-size: 16px; font-weight: 700; color: #00FFFF; margin: 4px 0; }
    .today-detail   { font-size: 12px; color: rgba(255,255,255,0.5); }

    .stat-pill {
        display: inline-block; padding: 4px 12px;
        border-radius: 99px; font-size: 12px; font-weight: 600;
        margin: 3px 4px;
    }
    .season-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 16px 18px;
        margin-bottom: 10px;
    }
    .season-year { font-size: 22px; font-weight: 800; color: #FFE66D; }
    .season-champ { font-size: 15px; color: white; font-weight: 600; margin: 4px 0 10px; }
    .season-award { font-size: 12px; color: rgba(255,255,255,0.55); margin: 3px 0; }

    .fact-card {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #00FFFF;
        border-radius: 0 12px 12px 0;
        padding: 14px 16px; margin-bottom: 10px;
    }
    .fact-icon { font-size: 20px; margin-bottom: 6px; }
    .fact-text { font-size: 13px; color: rgba(255,255,255,0.8); line-height: 1.6; }

    .hero-banner {
        background: linear-gradient(135deg, rgba(0,93,160,0.4), rgba(236,28,36,0.3));
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 20px; padding: 40px 30px;
        text-align: center; margin-bottom: 28px;
    }
    .hero-banner h1 { font-size: 44px; font-weight: 800; color: white; margin: 0 0 8px; }
    .hero-tagline    { font-size: 16px; color: rgba(255,255,255,0.65); margin: 0 0 6px; }
    .hero-byline     { font-size: 13px; color: rgba(255,255,255,0.4); }

    .ticker-bar {
        background: rgba(255,230,109,0.08);
        border: 1px solid rgba(255,230,109,0.2);
        border-radius: 8px; padding: 8px 16px;
        margin-bottom: 24px;
        display: flex; align-items: center; gap: 10px;
    }
    .ticker-label { font-size: 11px; font-weight: 700; color: #FFE66D;
                    text-transform: uppercase; letter-spacing: 1px; flex-shrink: 0; }
    .ticker-text  { font-size: 13px; color: rgba(255,255,255,0.75); }
    </style>
    """, unsafe_allow_html=True)

    # ── today ticker ─────────────────────────────────────────────
    today_str = datetime.now().strftime("%A, %d %B")
    st.markdown(f"""
    <div class="ticker-bar">
        <span class="ticker-label">📅 Today</span>
        <span class="ticker-text">{today_str} &nbsp;·&nbsp;
        IPL has 18 seasons of history in this app &nbsp;·&nbsp;
        278,205 balls analysed</span>
    </div>
    """, unsafe_allow_html=True)

    # ── hero banner ───────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <h1>🏏 Cricket Analytics</h1>
        <p class="hero-tagline">Smart Insights &nbsp;·&nbsp; Performance Analytics &nbsp;·&nbsp; Data Driven</p>
        <p class="hero-byline">Built by Aayush Tripathi — Cricketer turned Developer</p>
    </div>
    """, unsafe_allow_html=True)

    # ── today in IPL history ──────────────────────────────────────
    today_display = datetime.now().strftime("%d %B")
    st.markdown(
        f'<div class="home-section-title">📅 On This Day in IPL History — {today_display}</div>',
        unsafe_allow_html=True,
    )

    events = _today_history_events(data)

    if events:
        cols = st.columns(len(events))
        for i, ev in enumerate(events):
            with cols[i]:
                st.markdown(f"""
                <div class="today-card">
                    <div class="today-icon">{ev['icon']}</div>
                    <div class="today-headline">{ev['headline']}</div>
                    <div class="today-detail">{ev['detail']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="today-card" style="text-align:center;">
            <div class="today-icon">🏟️</div>
            <div class="today-headline">No IPL matches on this date historically</div>
            <div class="today-detail">But plenty of records to explore in the other sections</div>
        </div>
        """, unsafe_allow_html=True)

    # ── season hall of fame ───────────────────────────────────────
    st.markdown(
        '<div class="home-section-title">🏆 IPL Season Hall of Fame</div>',
        unsafe_allow_html=True,
    )

    seasons = sorted(SEASON_CHAMPIONS.keys(), reverse=True)[:6]
    col1, col2 = st.columns(2)
    for i, season in enumerate(seasons):
        champ  = SEASON_CHAMPIONS[season]
        orange = ORANGE_CAP.get(season, "—")
        purple = PURPLE_CAP.get(season, "—")
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="season-card">
                <div class="season-year">IPL {season}</div>
                <div class="season-champ">🏆 {champ}</div>
                <div class="season-award">🟠 Orange Cap: {orange}</div>
                <div class="season-award">🟣 Purple Cap: {purple}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── did you know ──────────────────────────────────────────────
    st.markdown(
        '<div class="home-section-title">💡 Did You Know?</div>',
        unsafe_allow_html=True,
    )

    # Pick 3 random facts, different each visit using minute as seed
    seed = int(datetime.now().strftime("%H%M")) // 10
    random.seed(seed)
    facts = random.sample(DID_YOU_KNOW, min(3, len(DID_YOU_KNOW)))

    fact_cols = st.columns(3)
    for i, (icon, text) in enumerate(facts):
        with fact_cols[i]:
            st.markdown(f"""
            <div class="fact-card">
                <div class="fact-icon">{icon}</div>
                <div class="fact-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── quick nav cards ───────────────────────────────────────────
    st.markdown(
        '<div class="home-section-title">🔥 Explore the App</div>',
        unsafe_allow_html=True,
    )

    nav_data = [
        ("📊", "Batter Profiles",   "703 batters, 18 seasons of data"),
        ("🏏", "Team HQ",           "All IPL franchises compared"),
        ("⚔️", "Head to Head",      "Batter vs bowler matchup stats"),
        ("🏟️", "Ground Report",     "59 venues rated & ranked"),
        ("🎯", "Bowling Attack",    "Economy, wickets, death overs"),
        ("🏆", "Pressure Cooker",   "Who performs in knockouts?"),
    ]

    c1, c2, c3 = st.columns(3)
    for i, (icon, title, desc) in enumerate(nav_data):
        col = [c1, c2, c3][i % 3]
        with col:
            st.markdown(f"""
            <div class="today-card" style="text-align:center;">
                <div style="font-size:28px; margin-bottom:8px;">{icon}</div>
                <div style="font-size:15px; font-weight:700; color:white; margin-bottom:4px;">{title}</div>
                <div style="font-size:12px; color:rgba(255,255,255,0.5);">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-top:30px; font-size:13px; color:rgba(255,255,255,0.3);'>
        🚀 Built with Streamlit &nbsp;·&nbsp; IPL data 2008–2025 &nbsp;·&nbsp; 278K deliveries
    </div>
    """, unsafe_allow_html=True)