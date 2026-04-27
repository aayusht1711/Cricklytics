import streamlit as st


def show_header():
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --cyan:   #00e5ff;
        --gold:   #ffd166;
        --red:    #ff4d6d;
        --green:  #06d6a0;
        --bg:     #080c10;
        --surf:   #0d1117;
        --border: rgba(255,255,255,0.08);
        --muted:  rgba(255,255,255,0.45);
        --text:   rgba(255,255,255,0.92);
    }

    html, body, [class*="css"], .stApp {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text) !important;
        background: var(--bg) !important;
        -webkit-font-smoothing: antialiased;
    }
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton  { display: none; }
    .block-container {
        padding: 1.5rem 2.5rem 4rem !important;
        max-width: 1200px !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(8,12,16,0.97) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        transition: border-color 0.2s;
    }
    div[data-baseweb="select"] > div:hover { border-color: var(--cyan) !important; }

    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--cyan) !important;
        box-shadow: 0 0 0 3px rgba(0,229,255,0.08) !important;
        outline: none !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, rgba(0,229,255,0.08), rgba(0,229,255,0.18)) !important;
        border: 1px solid rgba(0,229,255,0.4) !important;
        color: var(--cyan) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        border-radius: 8px !important;
        text-transform: uppercase;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0,229,255,0.18), rgba(0,229,255,0.32)) !important;
        box-shadow: 0 0 24px rgba(0,229,255,0.2) !important;
        transform: translateY(-1px) !important;
    }

    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 1rem 1.2rem !important;
    }
    div[data-testid="metric-container"] label {
        color: var(--muted) !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: var(--cyan) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    div[data-testid="stTabs"] button {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        color: var(--muted) !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--cyan) !important;
        border-bottom: 2px solid var(--cyan) !important;
    }

    div[data-testid="stRadio"] label {
        font-size: 13px !important;
        color: var(--muted) !important;
    }

    div[data-testid="stProgress"] > div {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 99px !important;
        height: 4px !important;
    }
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, var(--cyan), var(--green)) !important;
        border-radius: 99px !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        background: rgba(255,255,255,0.02) !important;
    }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,229,255,0.3); }

    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: 0.5px !important;
        color: var(--text) !important;
    }
    h2 { font-size: 24px !important; font-weight: 700 !important; }
    h3 { font-size: 18px !important; font-weight: 600 !important; }

    /* ═══════════════════════════════════════════════════
       .card  — used by ALL original components
    ═══════════════════════════════════════════════════ */
    .card {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 18px 20px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.09);
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }
    .card:hover {
        border-color: rgba(255,255,255,0.16);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    }
    .card h3 { color: var(--cyan) !important; margin-bottom: 8px; }
    .card p  { color: rgba(255,255,255,0.75); font-size: 14px; line-height: 1.6; margin: 4px 0; }
    .card b  { color: var(--text); }

    /* ═══════════════════════════════════════════════════
       Updated component styles (player, team, insights,
       live, predictor, commentator, home)
    ═══════════════════════════════════════════════════ */
    .player-profile-card {
        background: rgba(255,255,255,0.03); border-radius: 18px;
        padding: 22px 24px; margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .player-avatar {
        width: 56px; height: 56px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 800; flex-shrink: 0;
    }
    .player-name {
        font-size: 22px; font-weight: 800; color: white; margin: 0;
        font-family: 'Rajdhani', sans-serif; letter-spacing: 1px;
    }
    .role-badge {
        display: inline-block; padding: 3px 10px; border-radius: 99px;
        font-size: 11px; font-weight: 700; margin-top: 6px; letter-spacing: 0.5px;
    }
    .commentary-tag {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.06); border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 5px 12px; font-size: 12px;
        color: rgba(255,255,255,0.8); margin: 3px 3px 3px 0;
    }
    .stat-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-value { color: var(--text); font-size: 15px; font-weight: 600; font-family: 'Rajdhani', sans-serif; }

    .team-header {
        border-radius: 18px; padding: 22px 26px; margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03);
    }
    .team-name-title {
        font-size: 26px; font-weight: 800; color: white; margin: 0 0 4px;
        font-family: 'Rajdhani', sans-serif; letter-spacing: 1px;
    }
    .team-stat-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .team-stat-row:last-child { border-bottom: none; }
    .team-stat-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
    .team-stat-value { color: var(--text); font-size: 15px; font-weight: 600; font-family: 'Rajdhani', sans-serif; }
    .team-player-card {
        background: rgba(255,255,255,0.03); border-radius: 12px; padding: 12px 16px;
        margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.06);
        display: flex; justify-content: space-between; align-items: center;
        transition: border-color 0.2s, background 0.2s;
    }
    .team-player-card:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); }
    .team-rank { font-size: 18px; font-weight: 800; color: rgba(255,255,255,0.2); margin-right: 12px; font-family: 'Rajdhani', sans-serif; }
    .team-player-name { font-size: 14px; font-weight: 600; color: var(--text); }
    .team-player-stat { font-size: 12px; color: var(--muted); margin-top: 2px; }

    .insight-card {
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px; padding: 14px 18px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
        transition: border-color 0.2s, background 0.2s;
    }
    .insight-card:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); }
    .insight-rank { font-size: 22px; font-weight: 800; color: rgba(255,255,255,0.2); margin-right: 14px; font-family: 'Rajdhani', sans-serif; }
    .insight-name { font-size: 15px; font-weight: 600; color: var(--text); font-family: 'Rajdhani', sans-serif; }
    .insight-sub  { font-size: 12px; color: var(--muted); margin-top: 2px; }
    .insight-value { font-size: 18px; font-weight: 800; color: var(--cyan); font-family: 'Rajdhani', sans-serif; }

    .lv-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 14px; transition: border-color 0.2s, transform 0.2s; }
    .lv-card:hover { border-color: rgba(255,255,255,0.14); transform: translateY(-2px); }
    .lv-score-box { background: rgba(0,0,0,0.3); border-radius: 10px; padding: 12px 16px; margin: 10px 0; }
    .lv-score-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
    .lv-score-row:last-child { border-bottom: none; }
    .lv-badge { display: inline-block; font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 4px; letter-spacing: 0.5px; }
    .lv-live-dot { width: 8px; height: 8px; background: #FF4444; border-radius: 50%; display: inline-block; margin-right: 6px; box-shadow: 0 0 6px #FF4444; }
    .lv-team { color: var(--cyan); font-size: 17px; font-weight: 700; margin: 6px 0 2px; font-family: 'Rajdhani', sans-serif; }
    .lv-vs { color: rgba(255,255,255,0.25); font-size: 12px; margin: 0 0 6px; }
    .lv-status { color: var(--muted); font-size: 13px; margin: 6px 0 2px; }
    .lv-venue { color: rgba(255,255,255,0.25); font-size: 12px; margin: 0; }
    .lv-date { color: rgba(255,255,255,0.25); font-size: 11px; }
    .lv-runs { color: white; font-size: 18px; font-weight: 700; font-family: 'Rajdhani', sans-serif; }
    .lv-overs { color: rgba(255,255,255,0.35); font-size: 12px; font-weight: 400; }
    .lv-inning { color: var(--muted); font-size: 13px; }
    .lv-footer { margin-top: 28px; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.02); text-align: center; color: rgba(255,255,255,0.2); font-size: 11px; font-family: 'JetBrains Mono', monospace; }
    .lv-section-title { color: white; font-size: 18px; font-weight: 700; margin: 16px 0 10px; font-family: 'Rajdhani', sans-serif; }
    .lv-ended-label { color: rgba(255,255,255,0.25); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
    .lv-empty { text-align: center; padding: 40px 20px; }
    .lv-empty-icon { font-size: 48px; margin-bottom: 12px; }
    .lv-empty-title { color: var(--muted); font-size: 18px; margin-bottom: 6px; }
    .lv-empty-sub { color: rgba(255,255,255,0.25); font-size: 13px; }

    .pred-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px 22px; margin-bottom: 14px; }
    .metric-box { background: rgba(0,0,0,0.25); border-radius: 12px; padding: 16px 18px; text-align: center; border: 1px solid rgba(255,255,255,0.06); }
    .metric-val { font-size: 28px; font-weight: 800; color: var(--cyan); font-family: 'Rajdhani', sans-serif; }
    .metric-label { font-size: 11px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }
    .winner-banner { border-radius: 14px; padding: 22px; text-align: center; margin: 16px 0; }
    .winner-name { font-size: 26px; font-weight: 800; color: white; font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; }
    .winner-sub { font-size: 14px; color: var(--muted); margin-top: 6px; }
    .insight-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 13px; }
    .insight-row:last-child { border-bottom: none; }
    .insight-label { color: var(--muted); }
    .insight-value { color: var(--text); font-weight: 600; }

    .comm-hero { background: linear-gradient(135deg, rgba(0,0,0,0.4), rgba(255,107,107,0.1)); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 24px 26px; margin-bottom: 20px; }
    .comm-title { font-size: 28px; font-weight: 800; color: white; margin: 0 0 6px; font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; }
    .comm-sub { font-size: 13px; color: var(--muted); line-height: 1.6; }
    .match-info-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 16px 18px; margin-bottom: 16px; }
    .score-block { background: rgba(0,0,0,0.3); border-radius: 12px; padding: 16px 18px; text-align: center; }
    .score-runs { font-size: 32px; font-weight: 800; color: white; font-family: 'Rajdhani', sans-serif; }
    .score-team { font-size: 12px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }
    .score-extra { font-size: 11px; color: rgba(255,255,255,0.25); margin-top: 2px; }
    .commentary-output { background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 22px 24px; font-size: 14px; line-height: 1.9; color: rgba(255,255,255,0.85); white-space: pre-wrap; word-wrap: break-word; margin-top: 16px; }
    .mode-badge { display: inline-block; padding: 4px 14px; border-radius: 99px; font-size: 12px; font-weight: 600; background: rgba(0,229,255,0.08); color: var(--cyan); border: 1px solid rgba(0,229,255,0.25); margin-bottom: 14px; }

    .home-section-title { font-size: 20px; font-weight: 700; color: white; margin: 32px 0 14px; letter-spacing: 0.5px; font-family: 'Rajdhani', sans-serif; }
    .today-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 18px 20px; margin-bottom: 12px; transition: transform 0.2s, border-color 0.2s; }
    .today-card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,0.14); }
    .today-icon { font-size: 28px; margin-bottom: 6px; }
    .today-headline { font-size: 15px; font-weight: 700; color: var(--cyan); margin: 4px 0; font-family: 'Rajdhani', sans-serif; }
    .today-detail { font-size: 12px; color: var(--muted); }
    .season-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 16px 18px; margin-bottom: 10px; }
    .season-year { font-size: 22px; font-weight: 800; color: var(--gold); font-family: 'Rajdhani', sans-serif; }
    .season-champ { font-size: 15px; color: white; font-weight: 600; margin: 4px 0 10px; }
    .season-award { font-size: 12px; color: var(--muted); margin: 3px 0; }
    .fact-card { background: rgba(255,255,255,0.03); border-left: 3px solid var(--cyan); border-radius: 0 12px 12px 0; padding: 14px 16px; margin-bottom: 10px; }
    .fact-icon { font-size: 20px; margin-bottom: 6px; }
    .fact-text { font-size: 13px; color: rgba(255,255,255,0.8); line-height: 1.6; }
    .hero-banner { background: linear-gradient(135deg, rgba(0,93,160,0.35), rgba(236,28,36,0.25)); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 40px 30px; text-align: center; margin-bottom: 28px; }
    .hero-banner h1 { font-size: 44px; font-weight: 800; color: white; margin: 0 0 8px; font-family: 'Rajdhani', sans-serif; letter-spacing: 2px; }
    .hero-tagline { font-size: 16px; color: rgba(255,255,255,0.6); margin: 0 0 6px; }
    .hero-byline  { font-size: 13px; color: rgba(255,255,255,0.35); }
    .ticker-bar { background: rgba(255,230,109,0.06); border: 1px solid rgba(255,230,109,0.18); border-radius: 8px; padding: 8px 16px; margin-bottom: 24px; display: flex; align-items: center; gap: 10px; }
    .ticker-label { font-size: 11px; font-weight: 700; color: var(--gold); text-transform: uppercase; letter-spacing: 1px; flex-shrink: 0; }
    .ticker-text { font-size: 13px; color: rgba(255,255,255,0.65); }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:0 0 1.2rem;border-bottom:1px solid rgba(255,255,255,0.07);
                margin-bottom:1.5rem;">
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:40px;height:40px;border-radius:10px;flex-shrink:0;
                        background:linear-gradient(135deg,rgba(0,229,255,0.15),rgba(0,229,255,0.3));
                        border:1px solid rgba(0,229,255,0.3);
                        display:flex;align-items:center;justify-content:center;font-size:20px;">🏏</div>
            <div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;
                            color:white;letter-spacing:1.5px;text-transform:uppercase;line-height:1;">
                    Cricklytics
                </div>
                <div style="font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:0.05em;margin-top:3px;">
                    IPL Analytics · AI Commentary · ML Predictions
                </div>
            </div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                        border-radius:99px;padding:4px 12px;font-size:11px;
                        color:rgba(255,255,255,0.45);font-family:'JetBrains Mono',monospace;">
                278K <span style="color:#00e5ff;">deliveries</span>
            </div>
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                        border-radius:99px;padding:4px 12px;font-size:11px;
                        color:rgba(255,255,255,0.45);font-family:'JetBrains Mono',monospace;">
                18 <span style="color:#00e5ff;">seasons</span>
            </div>
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                        border-radius:99px;padding:4px 12px;font-size:11px;
                        color:rgba(255,255,255,0.45);font-family:'JetBrains Mono',monospace;">
                703 <span style="color:#00e5ff;">players</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def set_bg(image_url):
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background:
            linear-gradient(to bottom,
                rgba(8,12,16,0.93) 0%,
                rgba(8,12,16,0.78) 50%,
                rgba(8,12,16,0.93) 100%),
            url("{image_url}") no-repeat center center fixed;
        background-size: cover;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content:"";
        position:fixed;inset:0;
        backdrop-filter:blur(5px);
        -webkit-backdrop-filter:blur(5px);
        background:rgba(8,12,16,0.5);
        z-index:0;
    }}
    .block-container {{ position:relative; z-index:1; }}
    </style>
    """, unsafe_allow_html=True)
