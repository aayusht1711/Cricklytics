import streamlit as st

def show_team_view(data):

    st.markdown("<h2>🏆 Team Analysis</h2>", unsafe_allow_html=True)

    team = st.selectbox("Select Team", sorted(data['batting_team'].unique()))

    df = data[data['batting_team'] == team]

    # TEAM STATS
    total_runs = df['runs_batter'].sum()
    balls = len(df)
    sr = (total_runs / balls * 100) if balls > 0 else 0

    wickets = 0
    if 'player_dismissed' in data.columns:
        wickets = df['player_dismissed'].notna().sum()

    boundaries = (df['runs_batter'] == 4).sum()
    sixes = (df['runs_batter'] == 6).sum()

    # TEAM CARD
    st.markdown(f"""
    <div class='card'>
    🏏 <b>{team}</b><br><br>
    Total Runs: {total_runs}<br>
    Balls Played: {balls}<br>
    Strike Rate: {round(sr,2)}<br>
    Wickets Lost: {wickets}<br>
    Fours: {boundaries}<br>
    Sixes: {sixes}
    </div>
    """, unsafe_allow_html=True)

    # TOP BATTERS
    st.markdown("<h3>🔥 Top Batters</h3>", unsafe_allow_html=True)

    top_batters = df.groupby('batter')['runs_batter'].sum().sort_values(ascending=False).head(5)

    for player, runs in top_batters.items():
        st.markdown(f"""
        <div class='card'>
        🏏 {player} — {runs} runs
        </div>
        """, unsafe_allow_html=True)

    # BEST STRIKE RATE (min 200 balls)
    st.markdown("<h3>🚀 Most Aggressive Batters</h3>", unsafe_allow_html=True)

    agg = df.groupby('batter').agg({
        'runs_batter': 'sum',
        'balls_faced': 'sum'
    })

    agg = agg[agg['balls_faced'] > 200]

    if not agg.empty:
        agg['sr'] = agg['runs_batter'] / agg['balls_faced'] * 100
        top_sr = agg.sort_values(by='sr', ascending=False).head(5)

        for player, row in top_sr.iterrows():
            st.markdown(f"""
            <div class='card'>
            ⚡ {player} — SR: {round(row['sr'],2)}
            </div>
            """, unsafe_allow_html=True)