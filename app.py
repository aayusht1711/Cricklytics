import streamlit as st
import time
import pandas as pd
import matplotlib.pyplot as plt
 
from utils.data_loader import load_data
from components.header import show_header, set_bg
from components.player_view import show_player_view
from components.team_view import show_team_view
from components.insights_view import show_insights
from components.compare_view import show_compare_view
from components.venue_view import show_venue_view
from components.bowler_view import show_bowler_view
from components.knockout_view import show_knockout_view
from components.live_view import show_live_view
 
 
# ================================================================
# LOADER
# ================================================================
def cricket_loader():
    loader_html = """
    <style>
    .loader-container { text-align: center; margin-top: 120px; }
    .bat { font-size: 70px; display: inline-block; animation: swing 1s infinite ease-in-out; }
    @keyframes swing {
        0%   { transform: rotate(0deg); }
        50%  { transform: rotate(-35deg); }
        100% { transform: rotate(0deg); }
    }
    .ball {
        width: 35px; height: 35px; background: red; border-radius: 50%;
        display: inline-block; margin-left: 20px; position: relative;
    }
    .ball::before {
        content: ''; position: absolute; left: 50%;
        width: 2px; height: 100%; background: white; transform: translateX(-50%);
    }
    .text { font-size: 20px; margin-top: 20px; font-weight: bold; }
    </style>
    <div class="loader-container">
        <div class="bat">🏏</div>
        <div class="ball"></div>
        <div class="text">Preparing Match Insights...</div>
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
st.set_page_config(page_title="Cricket Analytics Dashboard", layout="wide")
 
# ================================================================
# SESSION STATE
# ================================================================
if "page" not in st.session_state:
    st.session_state.page = "Home"
 
# Loader only on first visit, not every Streamlit rerun
if "loader_done" not in st.session_state:
    cricket_loader()
    st.session_state.loader_done = True
 
# ================================================================
# CSV UPLOAD
# ================================================================
st.sidebar.markdown("### 📂 Upload Match CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
 
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, low_memory=False)
else:
    data = load_data()
 
# ================================================================
# HEADER
# ================================================================
show_header()
 
# ================================================================
# SIDEBAR MENU
# ================================================================
PAGES = [
    "Home",
    "🔴 Live Scores",
    "Player Analysis",
    "Team Analysis",
    "Insights",
    "Player Battle",
    "Venue Intelligence",
    "Bowler Analytics",
    "Knockout Filter",
]
 
if st.session_state.page not in PAGES:
    st.session_state.page = "Home"
 
menu = st.sidebar.selectbox(
    "Menu",
    PAGES,
    index=PAGES.index(st.session_state.page),
)
st.session_state.page = menu
 
# ================================================================
# BACKGROUND IMAGES
# ================================================================
BACKGROUND_IMAGES = {
    "Home":               "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "🔴 Live Scores":     "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "Player Analysis":    "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "Team Analysis":      "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Insights":           "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "Player Battle":      "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
    "Venue Intelligence": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "Bowler Analytics":   "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Knockout Filter":    "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff",
}
set_bg(BACKGROUND_IMAGES[menu])
 
# ================================================================
# HOME
# ================================================================
if menu == "Home":
    st.markdown("""
    <style>
    .hero {
        background-image: url("https://images.unsplash.com/photo-1593341646782-e0b495cff86d");
        background-size: cover; background-position: center;
        padding: 120px 20px; border-radius: 15px; text-align: center; color: white;
    }
    .hero h1 { font-size: 50px; font-weight: bold; }
    .hero p  { font-size: 20px; margin-top: 10px; }
    .btn {
        display: inline-block; padding: 10px 25px; margin: 15px;
        border-radius: 8px; background-color: white; color: black;
        font-weight: bold; text-decoration: none;
    }
    .section { margin-top: 50px; text-align: center; }
    .card {
        padding: 25px; border-radius: 15px;
        background: linear-gradient(135deg, #1f4037, #99f2c8);
        color: black; margin: 10px; transition: 0.3s;
    }
    .card:hover { transform: scale(1.05); }
    </style>
 
    <div class="hero">
        <h1>🏏 Cricket Analytics</h1>
        <p>Smart Insights • Performance Analytics • Data Driven</p>
        <p>Built by Aayush Tripathi</p>
        <a class="btn">Get Started</a>
        <a class="btn">Explore Stats</a>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("<div class='section'><h2>🔥 Features</h2></div>", unsafe_allow_html=True)
 
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="card">
            <h3>🔴 Live Scores</h3>
            <p>Real-time scores & upcoming matches</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="card">
            <h3>📊 Player Analysis</h3>
            <p>Deep dive into player performance stats</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="card">
            <h3>🏏 Team Analysis</h3>
            <p>Compare team stats easily</p>
        </div>""", unsafe_allow_html=True)
 
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("""<div class="card">
            <h3>🏟️ Venue Intelligence</h3>
            <p>Ground ratings, chase stats & venue specialists</p>
        </div>""", unsafe_allow_html=True)
    with col5:
        st.markdown("""<div class="card">
            <h3>🎯 Bowler Analytics</h3>
            <p>Economy by phase, dismissal types & death specialists</p>
        </div>""", unsafe_allow_html=True)
    with col6:
        st.markdown("""<div class="card">
            <h3>🏆 Knockout Filter</h3>
            <p>Who performs under pressure — knockouts vs league</p>
        </div>""", unsafe_allow_html=True)
 
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; font-size:18px;'>
        🚀 Built with Streamlit | Cricket Analytics Project
    </div>""", unsafe_allow_html=True)
 
# ================================================================
# LIVE SCORES
# ================================================================
elif menu == "🔴 Live Scores":
    show_live_view()
 
# ================================================================
# PLAYER ANALYSIS
# ================================================================
elif menu == "Player Analysis":
    show_player_view(data)
    st.markdown("### 📊 Advanced Player Stats")
    if "batter" in data.columns and "runs_batter" in data.columns:
        player = st.selectbox("Select Player for Advanced Stats", data["batter"].unique())
        df_p = data[data["batter"] == player]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Runs", int(df_p["runs_batter"].sum()))
        col2.metric("Balls Played", int(df_p["balls_faced"].sum()))
        balls = df_p["balls_faced"].sum()
        sr = (df_p["runs_batter"].sum() / balls) * 100 if balls > 0 else 0
        col3.metric("Strike Rate", round(sr, 2))
 
# ================================================================
# TEAM ANALYSIS
# ================================================================
elif menu == "Team Analysis":
    show_team_view(data)
 
# ================================================================
# INSIGHTS
# ================================================================
elif menu == "Insights":
    show_insights(data)
    st.markdown("### 🧠 Match Summary")
    if "runs_batter" in data.columns:
        st.metric("Total Runs", int(data["runs_batter"].sum()))
    if "bowler_wicket" in data.columns:
        st.metric("Total Wickets", int(data["bowler_wicket"].sum()))
    st.markdown("### 📈 Match Graphs")
    if "over" in data.columns and "runs_total" in data.columns:
        runs_over = data.groupby("over")["runs_total"].sum()
        fig, ax = plt.subplots()
        ax.plot(runs_over.index, runs_over.values)
        ax.set_title("Runs per Over")
        st.pyplot(fig)
    if "over" in data.columns and "bowler_wicket" in data.columns:
        wk_over = data.groupby("over")["bowler_wicket"].sum()
        fig2, ax2 = plt.subplots()
        ax2.bar(wk_over.index, wk_over.values)
        ax2.set_title("Wickets per Over")
        st.pyplot(fig2)
 
# ================================================================
# PLAYER BATTLE
# ================================================================
elif menu == "Player Battle":
    show_compare_view(data)
 
# ================================================================
# VENUE INTELLIGENCE
# ================================================================
elif menu == "Venue Intelligence":
    show_venue_view(data)
 
# ================================================================
# BOWLER ANALYTICS
# ================================================================
elif menu == "Bowler Analytics":
    show_bowler_view(data)
 
# ================================================================
# KNOCKOUT FILTER
# ================================================================
elif menu == "Knockout Filter":
    show_knockout_view(data)
 
