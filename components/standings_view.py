import streamlit as st
import pandas as pd

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

@st.cache_data
def _calculate_standings(data, season):
    season_df = data[data["season"] == season]
    if season_df.empty:
        return pd.DataFrame()
        
    match_df = season_df.drop_duplicates("match_id").copy()
    
    # Teams that played in this season
    teams = pd.concat([match_df["batting_team"], match_df["bowling_team"]]).unique()
    teams = [t for t in teams if pd.notna(t)]
    
    standings = []
    
    for team in teams:
        team_matches = match_df[(match_df["batting_team"] == team) | (match_df["bowling_team"] == team)]
        played = len(team_matches)
        
        wins = len(team_matches[team_matches["match_won_by"] == team])
        losses = len(team_matches[(team_matches["match_won_by"].notna()) & (team_matches["match_won_by"] != team)])
        nr = played - wins - losses
        
        points = (wins * 2) + nr
        
        # Simple NRR calculation based on available ball-by-ball
        team_batting = season_df[season_df["batting_team"] == team]
        runs_scored = team_batting["runs_total"].sum()
        balls_faced = team_batting["valid_ball"].sum()
        
        team_bowling = season_df[season_df["bowling_team"] == team]
        runs_conceded = team_bowling["runs_total"].sum()
        balls_bowled = team_bowling["valid_ball"].sum()
        
        overs_faced = balls_faced / 6 if balls_faced > 0 else 1
        overs_bowled = balls_bowled / 6 if balls_bowled > 0 else 1
        
        nrr = (runs_scored / overs_faced) - (runs_conceded / overs_bowled)
        
        standings.append({
            "Team": team,
            "M": played,
            "W": wins,
            "L": losses,
            "NR": nr,
            "Pts": points,
            "NRR": round(nrr, 3)
        })
        
    df_standings = pd.DataFrame(standings)
    df_standings = df_standings.sort_values(by=["Pts", "NRR"], ascending=[False, False]).reset_index(drop=True)
    df_standings.index += 1
    
    return df_standings

def show_standings_view(data):
    st.markdown("<h2>🏆 Season Standings</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(255,255,255,0.7);'>Dynamically calculated from ball-by-ball records</p>", unsafe_allow_html=True)
    
    seasons = sorted(data["season"].unique(), reverse=True)
    season = st.selectbox("Select Season", seasons)
    
    df_standings = _calculate_standings(data, season)
    
    if df_standings.empty:
        st.warning("No data found for this season.")
        return
        
    # Build HTML table
    table_html = "<table style='width:100%; border-collapse: collapse; font-family: DM Sans, sans-serif; color: white; margin-top: 10px;'>"
    table_html += "<tr style='border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left;'>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>POS</th>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>TEAM</th>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>M</th>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>W</th>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>L</th>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>NR</th>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>PTS</th>"
    table_html += "<th style='padding: 10px 5px; color: rgba(255,255,255,0.6); font-weight: normal;'>NRR</th>"
    table_html += "</tr>"
    
    for idx, row in df_standings.iterrows():
        team_color = TEAM_COLORS.get(row["Team"], "#FFF")
        
        is_top_4 = True if idx <= 4 else False
        glow = f"box-shadow: inset 0 0 15px {team_color}33; " if is_top_4 else ""
        border_l = f"border-left: 4px solid {team_color}; " if is_top_4 else "border-left: 4px solid transparent; "
        
        # Initials logo
        initials = "".join([p[0] for p in str(row["Team"]).split()[:2]]).upper()
        logo_html = f"<div style='min-width: 28px; height: 28px; border-radius: 50%; background: {team_color}33; border: 1px solid {team_color}; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; color: {team_color};'>{initials}</div>"
        
        table_html += f"<tr style='border-bottom: 1px solid rgba(255,255,255,0.05); {glow}'>"
        table_html += f"<td style='padding: 14px 5px; {border_l} font-weight: bold;'>{idx}</td>"
        
        table_html += f"<td style='padding: 14px 5px; display: flex; align-items: center; gap: 12px; font-weight: 600; color: {team_color};'>"
        table_html += f"{logo_html} <span>{row['Team']}</span>"
        table_html += f"</td>"
        
        table_html += f"<td style='padding: 14px 5px; font-size: 15px;'>{row['M']}</td>"
        table_html += f"<td style='padding: 14px 5px; color: #4ECDC4; font-weight: bold; font-size: 15px;'>{row['W']}</td>"
        table_html += f"<td style='padding: 14px 5px; color: #FF6B6B; font-size: 15px;'>{row['L']}</td>"
        table_html += f"<td style='padding: 14px 5px; font-size: 15px;'>{row['NR']}</td>"
        table_html += f"<td style='padding: 14px 5px; font-size: 18px; font-weight: 800; color: #FFE66D;'>{row['Pts']}</td>"
        
        nrr_color = "#4ECDC4" if row["NRR"] > 0 else "#FF6B6B"
        table_html += f"<td style='padding: 14px 5px; color: {nrr_color}; font-weight: bold; font-size: 14px;'>{row['NRR']}</td>"
        
        table_html += "</tr>"
        
    table_html += "</table>"
    
    st.markdown(f"<div class='card' style='padding: 15px; overflow-x: auto;'>{table_html}</div>", unsafe_allow_html=True)
