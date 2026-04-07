import streamlit as st

def show_compare_view(data):

    st.markdown("<h2>🎯 Batter vs Bowler Battle</h2>", unsafe_allow_html=True)

    # SELECT
    col1, col2 = st.columns(2)

    batter = col1.selectbox("Select Batter", sorted(data['batter'].unique()))
    bowler = col2.selectbox("Select Bowler", sorted(data['bowler'].unique()))

    df = data[(data['batter'] == batter) & (data['bowler'] == bowler)]

    if df.empty:
        st.warning("No matchup data available")
        return

    # BASIC STATS
    runs = df['runs_batter'].sum()
    balls = len(df)

    dismissals = 0
    if 'player_dismissed' in data.columns:
        dismissals = df['player_dismissed'].notna().sum()

    fours = (df['runs_batter'] == 4).sum()
    sixes = (df['runs_batter'] == 6).sum()

    sr = (runs / balls * 100) if balls > 0 else 0
    avg = (runs / dismissals) if dismissals > 0 else runs

    # MAIN CARD
    st.markdown(f"""
    <div class='card'>
    🏏 <b>{batter} vs {bowler}</b><br><br>
    Runs: {runs}<br>
    Balls: {balls}<br>
    Strike Rate: {round(sr,2)}<br>
    Average: {round(avg,2)}<br>
    Fours: {fours}<br>
    Sixes: {sixes}<br>
    Dismissals: {dismissals}
    </div>
    """, unsafe_allow_html=True)

    # INSIGHT LOGIC
    if dismissals > 0 and avg < 20:
        insight = f"🎯 {bowler} dominates this matchup"
    elif sr > 140:
        insight = f"🔥 {batter} attacks this bowler aggressively"
    elif sr > 120:
        insight = "⚖️ Balanced but batter slightly ahead"
    else:
        insight = "⚔️ Tight contest"

    st.markdown(f"""
    <div class='card'>
    💡 Insight: {insight}
    </div>
    """, unsafe_allow_html=True)