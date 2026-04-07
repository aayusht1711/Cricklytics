import streamlit as st
from utils.data_loader import load_data
from components.header import show_header, set_bg
from components.player_view import show_player_view
from components.team_view import show_team_view
from components.insights_view import show_insights
from components.compare_view import show_compare_view

# PAGE CONFIG
st.set_page_config(page_title="Cricket Analytics Dashboard", layout="wide")

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

# 🔥 BACKGROUND IMAGES (CRICKET ONLY — FINAL)
BACKGROUND_IMAGES = {
    "Player Analysis": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e",
    "Team Analysis": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2",
    "Insights": "https://images.unsplash.com/photo-1593341646782-e0b495cff86d",
    "Player Battle": "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff"
}

# ✅ APPLY BACKGROUND (VERY IMPORTANT POSITION)
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