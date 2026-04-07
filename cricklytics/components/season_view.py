import streamlit as st

def show_season_view(data):

    st.markdown("<h2>📅 Season Analytics</h2>", unsafe_allow_html=True)

    if 'season' not in data.columns:
        st.warning("No season data available")
        return

    season = st.selectbox("Select Season", sorted(data['season'].unique()))
    df = data[data['season'] == season]

    top = df.groupby('batter')['runs_batter'].sum().sort_values(ascending=False).head(5)

    for i, (player, runs) in enumerate(top.items(), start=1):
        st.markdown(f"""
        <div class='card'>
        🏏 <b>#{i} {player}</b><br>
        Runs: {runs}
        </div>
        """, unsafe_allow_html=True)