import streamlit as st

def show_insights(data):

    st.markdown("<h2>📊 Advanced Insights</h2>", unsafe_allow_html=True)

    # TOP RUN SCORERS
    top = data.groupby('batter')['runs_batter'].sum().sort_values(ascending=False).head(5)

    st.markdown("<h3>🏏 Top Run Scorers</h3>", unsafe_allow_html=True)

    for player, runs in top.items():
        st.markdown(f"<div class='card'>{player} — {runs} runs</div>", unsafe_allow_html=True)

    # CONSISTENT PLAYERS
    df = data.groupby('batter').agg({
        'runs_batter': 'sum',
        'balls_faced': 'sum'
    })

    df = df[df['balls_faced'] > 500]

    if not df.empty:
        df['avg'] = df['runs_batter'] / df['balls_faced']

        consistent = df.sort_values(by='avg', ascending=False).head(5)

        st.markdown("<h3>🎯 Most Consistent</h3>", unsafe_allow_html=True)

        for player, row in consistent.iterrows():
            st.markdown(f"<div class='card'>{player} — Avg: {round(row['avg'],2)}</div>", unsafe_allow_html=True)

        # AGGRESSIVE PLAYERS
        df['sr'] = df['runs_batter'] / df['balls_faced'] * 100
        aggressive = df.sort_values(by='sr', ascending=False).head(5)

        st.markdown("<h3>🚀 Most Aggressive</h3>", unsafe_allow_html=True)

        for player, row in aggressive.iterrows():
            st.markdown(f"<div class='card'>{player} — SR: {round(row['sr'],2)}</div>", unsafe_allow_html=True)