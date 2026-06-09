import streamlit as st
from utils.photo_helper import get_player_avatar_html, get_player_info

TEAM_COLORS = {
    "Mumbai Indians":"#005DA0","Chennai Super Kings":"#F7C010",
    "Royal Challengers Bengaluru":"#EC1C24","Royal Challengers Bangalore":"#EC1C24",
    "Kolkata Knight Riders":"#3A225D","Rajasthan Royals":"#EA1A85",
    "Sunrisers Hyderabad":"#F7700E","Delhi Capitals":"#0078BC",
    "Delhi Daredevils":"#0078BC","Punjab Kings":"#ED1B24",
    "Kings XI Punjab":"#ED1B24","Deccan Chargers":"#FDB933",
    "Gujarat Titans":"#1C4966","Lucknow Super Giants":"#A72056",
    "Gujarat Lions":"#E8461A","Rising Pune Supergiants":"#6F2DA8",
}

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

    # PHOTO / TEAM LOOKUP
    info_bat = get_player_info(batter)
    team_bat = info_bat["team"] if info_bat is not None else ""
    t_color_bat = TEAM_COLORS.get(team_bat, "#00FFFF")

    info_bowl = get_player_info(bowler)
    team_bowl = info_bowl["team"] if info_bowl is not None else ""
    t_color_bowl = TEAM_COLORS.get(team_bowl, "#FF6B6B")

    # Show photos below selector
    col1.markdown(get_player_avatar_html(batter, t_color_bat, size=80), unsafe_allow_html=True)
    col2.markdown(get_player_avatar_html(bowler, t_color_bowl, size=80), unsafe_allow_html=True)

    # PHASE STATS CALCULATION
    import pandas as pd
    df_phase = df.copy()
    df_phase["phase"] = pd.cut(df_phase["over"], bins=[-1, 5, 14, 20], labels=["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"])
    
    phase_rows_html = ""
    for phase_name in ["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"]:
        pdf = df_phase[df_phase["phase"] == phase_name]
        p_runs = int(pdf["runs_batter"].sum()) if not pdf.empty else 0
        p_balls = len(pdf)
        p_outs = int(pdf["player_dismissed"].notna().sum()) if "player_dismissed" in pdf.columns and not pdf.empty else 0
        p_sr = round((p_runs / p_balls * 100), 1) if p_balls > 0 else 0.0
        
        phase_rows_html += f"""
        <tr style='border-bottom: 1px solid rgba(255,255,255,0.04);'>
            <td style='padding:6px 0; font-weight:600; text-align:left;'>{phase_name}</td>
            <td style='text-align:center;'>{p_runs}</td>
            <td style='text-align:center;'>{p_balls}</td>
            <td style='text-align:center; font-weight:700; color:#00FFFF;'>{p_sr}</td>
            <td style='text-align:center; color:#FF6B6B; font-weight:700;'>{p_outs}</td>
        </tr>
        """

    # MAIN CARD
    avatar_bat_html = get_player_avatar_html(batter, t_color_bat, size=64, display_margin=False)
    avatar_bowl_html = get_player_avatar_html(bowler, t_color_bowl, size=64, display_margin=False)

    st.markdown(f"""
    <div class='card'>
        <div style='display:flex; align-items:center; justify-content:space-around; margin-bottom:20px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:15px;'>
            <div style='text-align:center;'>
                {avatar_bat_html}
                <div style='font-weight:700; color:{t_color_bat}; margin-top:8px;'>{batter}</div>
                <div style='font-size:11px; color:rgba(255,255,255,0.5);'>{team_bat if team_bat else 'Batter'}</div>
            </div>
            <div style='font-size:24px; font-weight:900; color:#FFE66D; font-style:italic;'>VS</div>
            <div style='text-align:center;'>
                {avatar_bowl_html}
                <div style='font-weight:700; color:{t_color_bowl}; margin-top:8px;'>{bowler}</div>
                <div style='font-size:11px; color:rgba(255,255,255,0.5);'>{team_bowl if team_bowl else 'Bowler'}</div>
            </div>
        </div>
        <table style='width:100%; color:white; font-size:15px;'>
            <tr>
                <td>🏏 Runs Scored</td><td><b>{runs}</b></td>
                <td>⚾ Balls Faced</td><td><b>{balls}</b></td>
            </tr>
            <tr>
                <td>⚡ Strike Rate</td><td><b>{round(sr,2)}</b></td>
                <td>📊 Average</td><td><b>{round(avg,2)}</b></td>
            </tr>
            <tr>
                <td>Four / Sixes</td><td><b>{fours} / {sixes}</b></td>
                <td>🎯 Dismissals</td><td><b style='color:#FF6B6B;'>{dismissals}</b></td>
            </tr>
        </table>
        
        <div style='margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;'>
            <h4 style='color:#FFE66D; margin: 0 0 10px 0; font-family:"Rajdhani", sans-serif; font-size: 16px; font-weight: 700;'>Matchup by Game Phase</h4>
            <table style='width:100%; color:white; font-size:13px; border-collapse: collapse;'>
                <thead>
                    <tr style='border-bottom: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.5); font-weight: 600;'>
                        <th style='text-align:left; padding: 4px 0;'>Phase</th>
                        <th style='text-align:center; padding: 4px 0;'>Runs</th>
                        <th style='text-align:center; padding: 4px 0;'>Balls</th>
                        <th style='text-align:center; padding: 4px 0;'>S/R</th>
                        <th style='text-align:center; padding: 4px 0; color:#FF6B6B;'>Outs</th>
                    </tr>
                </thead>
                <tbody>
                    {phase_rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # INSIGHT LOGIC
    if dismissals > 0 and avg < 20:
        insight = f"🎯 {bowler} dominates this matchup with {dismissals} dismissal{'s' if dismissals > 1 else ''} and keeping average under 20."
    elif sr > 140:
        insight = f"🔥 {batter} attacks this bowler aggressively with an explosive strike rate of {round(sr,1)}."
    elif sr > 120:
        insight = f"⚖️ Balanced contest, but {batter} scored at a healthy {round(sr,1)} strike rate."
    else:
        insight = "⚔️ Tight contest, bowler keeping the scoring rate under control."

    st.markdown(f"""
    <div class='card' style='border-left: 3px solid #FFE66D;'>
    💡 <b>Insight:</b> {insight}
    </div>
    """, unsafe_allow_html=True)