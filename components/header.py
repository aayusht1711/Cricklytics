import streamlit as st


def show_header():
    st.markdown("""
    <style>

    /* ── FONTS ─────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── CSS VARIABLES ──────────────────────────────────────────── */
    :root {
        --c-bg:        #080c10;
        --c-surface:   #0d1117;
        --c-border:    rgba(255,255,255,0.07);
        --c-border-hi: rgba(255,255,255,0.14);
        --c-cyan:      #00e5ff;
        --c-gold:      #ffd166;
        --c-red:       #ff4d6d;
        --c-green:     #06d6a0;
        --c-text:      rgba(255,255,255,0.92);
        --c-muted:     rgba(255,255,255,0.45);
        --c-dimmer:    rgba(255,255,255,0.25);
        --radius-sm:   8px;
        --radius-md:   14px;
        --radius-lg:   20px;
        --font-display:'Rajdhani', sans-serif;
        --font-body:   'DM Sans', sans-serif;
        --font-mono:   'JetBrains Mono', monospace;
    }

    /* ── GLOBAL RESET ───────────────────────────────────────────── */
    html, body, [class*="css"], .stApp {
        font-family: var(--font-body) !important;
        color: var(--c-text) !important;
        background: var(--c-bg) !important;
        -webkit-font-smoothing: antialiased;
    }

    /* ── HIDE STREAMLIT CHROME ──────────────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── MAIN CONTAINER ─────────────────────────────────────────── */
    .block-container {
        padding: 1.5rem 2.5rem 4rem !important;
        max-width: 1200px !important;
    }

    /* ── SIDEBAR ────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(8,12,16,0.97) !important;
        border-right: 1px solid var(--c-border) !important;
        backdrop-filter: blur(20px);
    }
    section[data-testid="stSidebar"] * {
        color: var(--c-text) !important;
        font-family: var(--font-body) !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stFileUploader label {
        color: var(--c-muted) !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── SELECTBOX ──────────────────────────────────────────────── */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--c-border-hi) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--c-text) !important;
        font-family: var(--font-body) !important;
        transition: border-color 0.2s;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: var(--c-cyan) !important;
    }
    div[data-baseweb="select"] svg { color: var(--c-muted) !important; }

    /* ── INPUT / TEXT INPUT ─────────────────────────────────────── */
    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--c-border-hi) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--c-text) !important;
        font-family: var(--font-mono) !important;
        font-size: 13px !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--c-cyan) !important;
        box-shadow: 0 0 0 3px rgba(0,229,255,0.08) !important;
        outline: none !important;
    }

    /* ── BUTTONS ────────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #00e5ff11, #00e5ff22) !important;
        border: 1px solid rgba(0,229,255,0.4) !important;
        color: var(--c-cyan) !important;
        font-family: var(--font-display) !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.55rem 1.5rem !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00e5ff22, #00e5ff44) !important;
        border-color: var(--c-cyan) !important;
        box-shadow: 0 0 24px rgba(0,229,255,0.2) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── METRICS ────────────────────────────────────────────────── */
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid var(--c-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 1.2rem !important;
    }
    div[data-testid="metric-container"] label {
        color: var(--c-muted) !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-family: var(--font-body) !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: var(--c-cyan) !important;
        font-family: var(--font-display) !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    /* ── TABS ───────────────────────────────────────────────────── */
    div[data-testid="stTabs"] button {
        font-family: var(--font-body) !important;
        font-size: 13px !important;
        color: var(--c-muted) !important;
        border-bottom: 2px solid transparent !important;
        padding: 8px 16px !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stTabs"] button:hover {
        color: var(--c-text) !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--c-cyan) !important;
        border-bottom-color: var(--c-cyan) !important;
        font-weight: 500 !important;
    }

    /* ── RADIO BUTTONS ──────────────────────────────────────────── */
    div[data-testid="stRadio"] label {
        font-family: var(--font-body) !important;
        font-size: 13px !important;
        color: var(--c-muted) !important;
        transition: color 0.2s;
    }
    div[data-testid="stRadio"] label:hover { color: var(--c-text) !important; }

    /* ── PROGRESS BAR ───────────────────────────────────────────── */
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, var(--c-cyan), var(--c-green)) !important;
        border-radius: 99px !important;
    }
    div[data-testid="stProgress"] > div {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 99px !important;
        height: 4px !important;
    }

    /* ── EXPANDER ───────────────────────────────────────────────── */
    div[data-testid="stExpander"] {
        border: 1px solid var(--c-border) !important;
        border-radius: var(--radius-md) !important;
        background: rgba(255,255,255,0.02) !important;
    }
    div[data-testid="stExpander"] summary {
        font-family: var(--font-body) !important;
        font-size: 13px !important;
        color: var(--c-muted) !important;
        padding: 12px 16px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: var(--c-text) !important;
    }

    /* ── SPINNER ────────────────────────────────────────────────── */
    div[data-testid="stSpinner"] p {
        font-family: var(--font-body) !important;
        color: var(--c-muted) !important;
        font-size: 13px !important;
    }

    /* ── ALERTS ─────────────────────────────────────────────────── */
    div[data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--c-border-hi) !important;
        font-family: var(--font-body) !important;
        font-size: 13px !important;
    }

    /* ── FILE UPLOADER ──────────────────────────────────────────── */
    div[data-testid="stFileUploader"] {
        border: 1px dashed var(--c-border-hi) !important;
        border-radius: var(--radius-md) !important;
        background: rgba(255,255,255,0.02) !important;
        padding: 8px !important;
        transition: border-color 0.2s;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(0,229,255,0.3) !important;
    }

    /* ── SCROLLBAR ──────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0,229,255,0.3);
    }

    /* ── GLOBAL CARD CLASS ──────────────────────────────────────── */
    .card {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--c-border);
        border-radius: var(--radius-lg);
        padding: 20px 22px;
        margin: 10px 0;
        transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
        position: relative;
        overflow: hidden;
    }
    .card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg,
            transparent, rgba(255,255,255,0.08), transparent);
    }
    .card:hover {
        border-color: var(--c-border-hi);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    /* ── HEADER BAR ─────────────────────────────────────────────── */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 0 1.5rem;
        border-bottom: 1px solid var(--c-border);
        margin-bottom: 1.5rem;
    }
    .app-header-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .app-logo {
        width: 40px; height: 40px;
        background: linear-gradient(135deg, #00e5ff22, #00e5ff44);
        border: 1px solid rgba(0,229,255,0.3);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }
    .app-name {
        font-family: var(--font-display);
        font-size: 22px;
        font-weight: 700;
        color: var(--c-text);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        line-height: 1;
    }
    .app-tagline {
        font-size: 11px;
        color: var(--c-muted);
        letter-spacing: 0.05em;
        margin-top: 3px;
    }
    .app-header-right {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .header-pill {
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--c-border-hi);
        border-radius: 99px;
        padding: 4px 12px;
        font-size: 11px;
        color: var(--c-muted);
        font-family: var(--font-mono);
        letter-spacing: 0.02em;
    }
    .header-pill span {
        color: var(--c-cyan);
        font-weight: 500;
    }

    /* ── PAGE TITLE STYLE ───────────────────────────────────────── */
    h1, h2, h3, h4 {
        font-family: var(--font-display) !important;
        letter-spacing: 0.5px !important;
        color: var(--c-text) !important;
    }
    h2 { font-size: 24px !important; font-weight: 700 !important; }
    h3 { font-size: 18px !important; font-weight: 600 !important; }

    /* ── DIVIDERS ───────────────────────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1px solid var(--c-border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── SIDEBAR BOTTOM BYLINE ──────────────────────────────────── */
    .sidebar-byline {
        position: fixed;
        bottom: 16px;
        left: 0;
        width: 260px;
        text-align: center;
        font-size: 11px;
        color: var(--c-dimmer);
        font-family: var(--font-mono);
        letter-spacing: 0.03em;
    }

    /* ── ANIMATED GRADIENT BORDER on active card ────────────────── */
    @keyframes borderGlow {
        0%   { box-shadow: 0 0 0 0 rgba(0,229,255,0); }
        50%  { box-shadow: 0 0 20px 2px rgba(0,229,255,0.12); }
        100% { box-shadow: 0 0 0 0 rgba(0,229,255,0); }
    }
    .card-glow {
        animation: borderGlow 3s ease-in-out infinite;
    }

    /* ── TEXTAREA ───────────────────────────────────────────────── */
    textarea {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid var(--c-border-hi) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--c-text) !important;
        font-family: var(--font-mono) !important;
        font-size: 12px !important;
        resize: vertical !important;
    }

    /* ── PYPLOT FIGURES – transparent background ─────────────────  */
    .stPlotlyChart, .stPyplot { background: transparent !important; }

    /* stImage border radius */
    img { border-radius: var(--radius-md); }

    /* ── SIDEBAR NAV SELECTED STATE ─────────────────────────────── */
    div[data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(0,229,255,0.08) !important;
        border-left: 2px solid var(--c-cyan) !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ── top header bar ───────────────────────────────────────────
    st.markdown("""
    <div class="app-header">
        <div class="app-header-left">
            <div class="app-logo">🏏</div>
            <div>
                <div class="app-name">Cricklytics</div>
                <div class="app-tagline">IPL Analytics · AI Commentary · ML Predictions</div>
            </div>
        </div>
        <div class="app-header-right">
            <div class="header-pill">278K <span>deliveries</span></div>
            <div class="header-pill">18 <span>seasons</span></div>
            <div class="header-pill">703 <span>players</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def set_bg(image_url):
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background:
            linear-gradient(to bottom,
                rgba(8,12,16,0.92) 0%,
                rgba(8,12,16,0.80) 40%,
                rgba(8,12,16,0.92) 100%),
            url("{image_url}") no-repeat center center fixed;
        background-size: cover;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        background: rgba(8,12,16,0.55);
        z-index: 0;
    }}
    .block-container {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """, unsafe_allow_html=True)
