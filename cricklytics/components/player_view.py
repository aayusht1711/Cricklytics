import streamlit as st
import matplotlib.pyplot as plt
from utils.analysis import player_stats, player_trend

def show_player_view(data):

    st.markdown("<h2>📊 Player Analysis</h2>", unsafe_allow_html=True)

    player = st.selectbox("Select Player", sorted(data['batter'].unique()))
    runs, sr = player_stats(data, player)

    st.markdown(f"""
    <div class='card'>
        <h3 style='color:#00FFFF;'>🏏 {player}</h3>
        <p>Total Runs: {runs}</p>
        <p>Strike Rate: {round(sr,2)}</p>
    </div>
    """, unsafe_allow_html=True)

    trend = player_trend(data, player)

    fig, ax = plt.subplots(figsize=(10,5))
    trend.plot(ax=ax, linewidth=3, marker='o')

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    ax.grid(True, linestyle="--", alpha=0.6)

    st.pyplot(fig)