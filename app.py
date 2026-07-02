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
from components.drs_view import show_drs_view
from components.scouting_view import show_scouting_view
from components.whatif_view import show_whatif_view
from components.dreamxi_view import show_dreamxi_view
from components.squad_view import show_squad_view
from components.home_view import DID_YOU_KNOW
from components.quiz_view import show_quiz_view
from components.season_view import show_season_view
from components.story_view import show_story_view
from components.dna_view import show_dna_view
from components.clutch_view import show_clutch_view
from components.three_background import show_3d_background
from components.standings_view import show_standings_view


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
.text { font-size:20px; margin-top:20px; font-weight:bold; }
</style>
<div class="loader-container">
<div class="bat">🏏</div>
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
from PIL import Image
st.set_page_config(
    page_title="Cricket Analytics — Aayush Tripathi",
    page_icon=Image.open("app_icon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "loader_done" not in st.session_state:
    cricket_loader()
    st.session_state.loader_done = True

# ================================================================
# DATA FORMAT SELECTOR
# ================================================================
st.sidebar.markdown("### 🌍 Select Format / League")
format_options = [
    "IPL", "BBL", "WBBL", "PSL", "CPL", "Hundred_Mens", "Hundred_Womens",
    "Mens_T20I", "Mens_ODI", "Mens_Test",
    "Womens_T20I", "Womens_ODI", "Womens_Test"
]
selected_format = st.sidebar.selectbox("Select Format", format_options, label_visibility="collapsed")

if selected_format in ["Mens_Test", "Womens_Test"]:
    from components.test_view import show_test_view
    show_test_view()
    st.stop()

# ================================================================
# DATA
# ================================================================
st.sidebar.markdown("### 📂 Upload Custom CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
data = pd.read_csv(uploaded_file, low_memory=False) if uploaded_file else load_data(selected_format)

# ================================================================
# HEADER
# ================================================================
show_header(data, selected_format)
# show_3d_background()

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
    "📅 Season Analytics", "🏆 Season Standings", "Insights", "Player Battle", "Venue Intelligence",
    "Bowler Analytics", "Knockout Filter", "🤖 ML Predictor",
    "🎙️ AI Commentator", "🔍 DRS Analytics",
    "🧠 AI Scouting Report", "🔀 What If Simulator", "🏆 Dream XI", "🏆 Trivia Quiz",
    "🎬 Match Story", "🧬 Player DNA", "⚡ Clutch Factor",
    "👥 2026 Squads",
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
    "📅 Season Analytics": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "🏆 Season Standings": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Insights":           "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "Player Battle":      "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "Venue Intelligence": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "Bowler Analytics":   "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Knockout Filter":    "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "🤖 ML Predictor":      "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    "🎙️ AI Commentator":   "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "🔍 DRS Analytics":     "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "🧠 AI Scouting Report": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "🔀 What If Simulator":  "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    "🏆 Dream XI":           "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "🏆 Trivia Quiz":        "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "🎬 Match Story":        "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "🧬 Player DNA":         "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "⚡ Clutch Factor":      "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    "👥 2026 Squads":        "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
}
set_bg(BG[menu])

# ================================================================
# ROUTING
# ================================================================
if   menu == "Home":               show_home(data)
elif menu == "🔴 Live Scores":     show_live_view()
elif menu == "Player Analysis":    show_player_view(data)
elif menu == "Team Analysis":      show_team_view(data)
elif menu == "📅 Season Analytics": show_season_view(data)
elif menu == "🏆 Season Standings": show_standings_view(data)
elif menu == "Insights":           show_insights(data)
elif menu == "Player Battle":      show_compare_view(data)
elif menu == "Venue Intelligence": show_venue_view(data)
elif menu == "Bowler Analytics":   show_bowler_view(data)
elif menu == "Knockout Filter":    show_knockout_view(data)
elif menu == "🤖 ML Predictor":   show_predictor_view(data)
elif menu == "🎙️ AI Commentator": show_commentator_view(data)
elif menu == "🔍 DRS Analytics":      show_drs_view(data)
elif menu == "🧠 AI Scouting Report": show_scouting_view(data)
elif menu == "🔀 What If Simulator":  show_whatif_view(data)
elif menu == "🏆 Dream XI":           show_dreamxi_view(data)
elif menu == "🏆 Trivia Quiz":        show_quiz_view(data)
elif menu == "🎬 Match Story":        show_story_view(data)
elif menu == "🧬 Player DNA":         show_dna_view(data)
elif menu == "⚡ Clutch Factor":      show_clutch_view(data)
elif menu == "👥 2026 Squads":        show_squad_view(data)