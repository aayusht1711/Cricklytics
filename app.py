import streamlit as st
import time
from utils.data_loader import load_data
from components.header import show_header, set_bg
from components.player_view import show_player_view
from components.team_view import show_team_view
from components.insights_view import show_insights
from components.compare_view import show_compare_view

# ---------------- LOADER ----------------
def cricket_loader():
    loader_html = """
    <style>
    .loader-container {
        text-align: center;
        margin-top: 120px;
    }

    .bat {
        font-size: 70px;
        display: inline-block;
        animation: swing 1s infinite ease-in-out;
    }

    @keyframes swing {
        0% { transform: rotate(0deg); }
        50% { transform: rotate(-35deg); }
        100% { transform: rotate(0deg); }
    }

    .ball {
        font-size: 40px;
        position: relative;
        display: inline-block;
        animation: moveBall 1s infinite linear;
    }

    @keyframes moveBall {
        0% { left: -120px; }
        50% { left: 0px; }
        100% { left: 120px; }
    }

    .text {
        font-size: 20px;
        margin-top: 20px;
        font-weight: bold;
    }
    </style>

    <div class="loader-container">
        <div class="bat">🏏</div>
        <div class="ball">🏐</div>
        <div class="text">Preparing Match Insights...</div>
    </div>
    """

    placeholder = st.empty()
    placeholder.markdown(loader_html, unsafe_allow_html=True)

    progress = st.progress(0)

    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)

    placeholder.empty()
    progress.empty()


# PAGE CONFIG
st.set_page_config(page_title="Cricket Analytics Dashboard", layout="wide")

# 🔥 ADD THIS LINE ONLY
cricket_loader()

# LOAD DATA
data = load_data()

# HEADER
show_header()

# MENU
menu = st.sidebar.selectbox("Menu", [
    "Player Analysis",
    "Team Analysis",
    "Insights",
    "Player Battle"
])


BACKGROUND_IMAGES = {
    "Player Analysis": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "Team Analysis": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Insights": "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "Player Battle": "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff"
}


set_bg(BACKGROUND_IMAGES[menu])

# ROUTING
if menu == "Player Analysis":
    show_player_view(data)

elif menu == "Team Analysis":
    show_team_view(data)

elif menu == "Insights":
    show_insights(data)

elif menu == "Player Battle":
    show_compare_view(data)
