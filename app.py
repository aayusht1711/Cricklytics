import streamlit as st
import time
import pandas as pd
import random

from utils.data_loader import load_data
from components.header import show_header, set_bg
from components.home_view import show_home
from components.player_view import show_player_view
from components.team_view import show_team_view
from components.insights_view import show_insights
from components.compare_view import show_compare_view
from components.venue_view import show_venue_view
from components.bowler_view import show_bowler_view
from components.knockout_view import show_knockout_view
from components.live_view import show_live_view
from components.predictor_view import show_predictor_view
from components.commentator_view import show_commentator_view
from components.home_view import DID_YOU_KNOW


# ================================================================
# LOADER
# ================================================================
def cricket_loader():
    loader_html = """
    <style>
    .loader-container { text-align:center; margin-top:120px; }
    .bat { font-size:70px; display:inline-block;
           animation:swing 1s infinite ease-in-out; }
    @keyframes swing {
        0%   { transform:rotate(0deg); }
        50%  { transform:rotate(-35deg); }
        100% { transform:rotate(0deg); }
    }
    .ball { width:35px; height:35px; background:red; border-radius:50%;
            display:inline-block; margin-left:20px; position:relative; }
    .ball::before { content:''; position:absolute; left:50%;
                    width:2px; height:100%; background:white;
                    transform:translateX(-50%); }
    .text { font-size:20px; margin-top:20px; font-weight:bold; }
    </style>
    <div class="loader-container">
        <div class="bat">🏏</div><div class="ball"></div>
        <div class="text">Loading the crease...</div>
    </div>
    """
    ph = st.empty()
    ph.markdown(loader_html, unsafe_allow_html=True)
    bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        bar.progress(i + 1)
    ph.empty()
    bar.empty()


# ================================================================
# PAGE CONFIG
# ================================================================
st.set_page_config(
    page_title="Cricket Analytics — Aayush Tripathi",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "loader_done" not in st.session_state:
    cricket_loader()
    st.session_state.loader_done = True

# ================================================================
# DATA
# ================================================================
st.sidebar.markdown("### 📂 Upload Match CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
data = pd.read_csv(uploaded_file, low_memory=False) if uploaded_file else load_data()

# ================================================================
# HEADER
# ================================================================
show_header()

# ================================================================
# SIDEBAR DID YOU KNOW
# ================================================================
st.sidebar.markdown("---")
random.seed(int(time.time()) // 300)
fact_icon, fact_text = random.choice(DID_YOU_KNOW)
st.sidebar.markdown(f"""
<div style='background:rgba(0,255,255,0.06);border-left:3px solid #00FFFF;
     border-radius:0 10px 10px 0;padding:10px 12px;margin:4px 0 12px;'>
    <div style='font-size:16px;margin-bottom:4px;'>{fact_icon}</div>
    <div style='font-size:12px;color:rgba(255,255,255,0.75);line-height:1.5;'>
        {fact_text}
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# ================================================================
# MENU
# ================================================================
PAGES = [
    "Home", "🔴 Live Scores", "Player Analysis", "Team Analysis",
    "Insights", "Player Battle", "Venue Intelligence",
    "Bowler Analytics", "Knockout Filter", "🤖 ML Predictor",
    "🎙️ AI Commentator",
]

if st.session_state.page not in PAGES:
    st.session_state.page = "Home"

menu = st.sidebar.selectbox(
    "Navigate", PAGES,
    index=PAGES.index(st.session_state.page),
)
st.session_state.page = menu

# ================================================================
# BACKGROUND
# ================================================================
BG = {
    "Home":               "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "🔴 Live Scores":     "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "Player Analysis":    "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "Team Analysis":      "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Insights":           "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "Player Battle":      "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "Venue Intelligence": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "Bowler Analytics":   "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Knockout Filter":    "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "🤖 ML Predictor":   "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    "🎙️ AI Commentator": "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
}
set_bg(BG[menu])

# ================================================================
# ROUTING
# ================================================================
if   menu == "Home":               show_home(data)
elif menu == "🔴 Live Scores":     show_live_view()
elif menu == "Player Analysis":    show_player_view(data)
elif menu == "Team Analysis":      show_team_view(data)
elif menu == "Insights":           show_insights(data)
elif menu == "Player Battle":      show_compare_view(data)
elif menu == "Venue Intelligence": show_venue_view(data)
elif menu == "Bowler Analytics":   show_bowler_view(data)
elif menu == "Knockout Filter":    show_knockout_view(data)
elif menu == "🤖 ML Predictor":   show_predictor_view(data)
elif menu == "🎙️ AI Commentator": show_commentator_view(data)
