import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

SEASON_DETAILS = {
    "2008":    {"champion": "Rajasthan Royals", "runner_up": "Chennai Super Kings", "orange_cap": "SE Marsh (616)", "purple_cap": "Sohail Tanvir (22)"},
    "2007/08": {"champion": "Rajasthan Royals", "runner_up": "Chennai Super Kings", "orange_cap": "SE Marsh (616)", "purple_cap": "Sohail Tanvir (22)"},
    "2009":    {"champion": "Deccan Chargers", "runner_up": "Royal Challengers Bangalore", "orange_cap": "ML Hayden (572)", "purple_cap": "RP Singh (23)"},
    "2009/10": {"champion": "Chennai Super Kings", "runner_up": "Mumbai Indians", "orange_cap": "SR Tendulkar (618)", "purple_cap": "PP Ojha (21)"},
    "2010":    {"champion": "Chennai Super Kings", "runner_up": "Mumbai Indians", "orange_cap": "SR Tendulkar (618)", "purple_cap": "PP Ojha (21)"},
    "2011":    {"champion": "Chennai Super Kings", "runner_up": "Royal Challengers Bangalore", "orange_cap": "CH Gayle (608)", "purple_cap": "SL Malinga (28)"},
    "2012":    {"champion": "Kolkata Knight Riders", "runner_up": "Chennai Super Kings", "orange_cap": "CH Gayle (733)", "purple_cap": "M Morkel (25)"},
    "2013":    {"champion": "Mumbai Indians", "runner_up": "Chennai Super Kings", "orange_cap": "MEK Hussey (733)", "purple_cap": "DJ Bravo (32)"},
    "2014":    {"champion": "Kolkata Knight Riders", "runner_up": "Kings XI Punjab", "orange_cap": "RV Uthappa (660)", "purple_cap": "MM Sharma (23)"},
    "2015":    {"champion": "Mumbai Indians", "runner_up": "Chennai Super Kings", "orange_cap": "DA Warner (562)", "purple_cap": "DJ Bravo (26)"},
    "2016":    {"champion": "Sunrisers Hyderabad", "runner_up": "Royal Challengers Bangalore", "orange_cap": "V Kohli (973)", "purple_cap": "B Kumar (23)"},
    "2017":    {"champion": "Mumbai Indians", "runner_up": "Rising Pune Supergiant", "orange_cap": "DA Warner (641)", "purple_cap": "B Kumar (26)"},
    "2018":    {"champion": "Chennai Super Kings", "runner_up": "Sunrisers Hyderabad", "orange_cap": "KS Williamson (735)", "purple_cap": "AJ Tye (24)"},
    "2019":    {"champion": "Mumbai Indians", "runner_up": "Chennai Super Kings", "orange_cap": "DA Warner (692)", "purple_cap": "Imran Tahir (26)"},
    "2020/21": {"champion": "Mumbai Indians", "runner_up": "Delhi Capitals", "orange_cap": "KL Rahul (676)", "purple_cap": "K Rabada (32)"},
    "2021":    {"champion": "Chennai Super Kings", "runner_up": "Kolkata Knight Riders", "orange_cap": "RD Gaikwad (635)", "purple_cap": "HV Patel (32)"},
    "2022":    {"champion": "Gujarat Titans", "runner_up": "Rajasthan Royals", "orange_cap": "JC Buttler (863)", "purple_cap": "YS Chahal (27)"},
    "2023":    {"champion": "Chennai Super Kings", "runner_up": "Gujarat Titans", "orange_cap": "Shubman Gill (890)", "purple_cap": "Mohammed Shami (28)"},
    "2024":    {"champion": "Kolkata Knight Riders", "runner_up": "Sunrisers Hyderabad", "orange_cap": "V Kohli (741)", "purple_cap": "HV Patel (24)"},
    "2025":    {"champion": "Royal Challengers Bengaluru", "runner_up": "Sunrisers Hyderabad", "orange_cap": "B Sai Sudharsan (759)", "purple_cap": "M Prasidh Krishna (25)"},
}

BASE = dict(template="plotly_dark")
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(14,17,23,0.8)",
    font=dict(family="DM Sans, sans-serif", color="white"),
    margin=dict(l=20, r=20, t=50, b=20),
)

def _fig(fig, title="", **kw):
    fig.update_layout(title=title, **LAYOUT, **kw)
    return fig

def get_cap_winner_html(cap_text, label, color):
    try:
        player_name = cap_text.split(" (")[0].strip()
        stats_val = cap_text.split(" (")[1].replace(")", "").strip()
    except Exception:
        player_name = cap_text
        stats_val = ""
    
    info = get_player_info(player_name)
    team_color = color
    team_name = "IPL Player"
    if info is not None:
        team_name = info.get("team", "Unknown Team")
        team_color = TEAM_COLORS.get(team_name, color)
        player_name = info.get("name", player_name)

    avatar_html = get_player_avatar_html(player_name, team_color, size=80, display_margin=False)
    
    return f"""
    <div style='background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-top:3px solid {team_color}; border-radius:14px; padding:16px; text-align:center; height: 100%;'>
        <div style='font-size:11px; text-transform:uppercase; color:rgba(255,255,255,0.5); font-weight:700; margin-bottom:8px;'>{label}</div>
        <div style='display:flex; justify-content:center; margin-bottom:10px;'>
            {avatar_html}
        </div>
        <div style='color:white; font-size:15px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{player_name}</div>
        <div style='font-size:11px; color:rgba(255,255,255,0.4); margin: 2px 0 6px 0;'>{team_name}</div>
        <div style='color:#FFE66D; font-size:18px; font-weight:800;'>{stats_val}</div>
    </div>
    """

def get_team_card_html(team_name, label, border_color):
    t_color = TEAM_COLORS.get(team_name, border_color)
    return f"""
    <div style='background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-left:5px solid {t_color}; border-radius:14px; padding:20px; height: 100%; display:flex; align-items:center;'>
        <div>
            <div style='font-size:11px; text-transform:uppercase; color:rgba(255,255,255,0.5); font-weight:700; margin-bottom:4px;'>{label}</div>
            <div style='color:white; font-size:22px; font-weight:800; font-family:"Rajdhani", sans-serif; letter-spacing:0.5px;'>{team_name}</div>
            <div style='font-size:12px; color:{t_color}; font-weight:600; margin-top:4px;'>IPL Franchise</div>
        </div>
    </div>
    """

def show_season_view(data):
    st.markdown("<h2>📅 Season Analytics</h2>", unsafe_allow_html=True)

    if 'season' not in data.columns:
        st.warning("No season data available in the loaded dataset.")
        return

    all_seasons = sorted(data['season'].unique(), reverse=True)
    
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        season = st.selectbox("Select Season to Analyze", all_seasons)
    
    df = data[data['season'] == season]
    
    # Basic aggregation metrics
    total_matches = int(df['match_id'].nunique())
    total_runs = int(df['runs_total'].sum())
    total_sixes = int((df['runs_batter'] == 6).sum())
    total_wickets = int((df['bowler_wicket'] == 1).sum())

    # Row of Metrics
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Matches", f"{total_matches:,}")
    c2.metric("Total Runs Scored", f"{total_runs:,}")
    c3.metric("Total Sixes", f"{total_sixes:,}")
    c4.metric("Total Wickets Taken", f"{total_wickets:,}")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Champions & Caps", "🏏 Batting Leaders", "🎯 Bowling Leaders", "📊 Team Performance", "📈 Scoring Trend"
    ])

    # Tab 1: Champions & Caps
    with tab1:
        details = SEASON_DETAILS.get(str(season))
        if details:
            st.markdown("<h3 style='margin: 15px 0 10px; font-family:\"Rajdhani\", sans-serif; font-weight:700;'>Season Champions & Key Awards</h3>", unsafe_allow_html=True)
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1:
                st.markdown(get_team_card_html(details["champion"], "Champions", "#FFE66D"), unsafe_allow_html=True)
            with col_ch2:
                st.markdown(get_team_card_html(details["runner_up"], "Runners-up", "#4ECDC4"), unsafe_allow_html=True)
            
            st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown(get_cap_winner_html(details["orange_cap"], "Orange Cap Winner", "#F7700E"), unsafe_allow_html=True)
            with col_c2:
                st.markdown(get_cap_winner_html(details["purple_cap"], "Purple Cap Winner", "#A72056"), unsafe_allow_html=True)
        else:
            st.info("Award details not pre-calculated for this season format, but leaderboards below show the top contributors!")

    # Tab 2: Batting Leaderboard
    with tab2:
        st.markdown("<h3 style='margin: 15px 0 10px; font-family:\"Rajdhani\", sans-serif; font-weight:700;'>Top 5 Run Scorers</h3>", unsafe_allow_html=True)
        balls_col = "valid_ball" if "valid_ball" in df.columns else "runs_batter"
        bat_stats = df.groupby("batter").agg(
            runs=("runs_batter", "sum"),
            balls=(balls_col, "sum"),
            sixes=("runs_batter", lambda x: (x == 6).sum()),
            fours=("runs_batter", lambda x: (x == 4).sum())
        ).reset_index()
        bat_stats["sr"] = (bat_stats["runs"] / bat_stats["balls"] * 100).round(1)
        top_batters = bat_stats.sort_values("runs", ascending=False).head(5)

        cols = st.columns(5)
        for i, (_, row) in enumerate(top_batters.iterrows()):
            info = get_player_info(row["batter"])
            team = info["team"] if info else "IPL Player"
            color = TEAM_COLORS.get(team, "#00FFFF")
            avatar_html = get_player_avatar_html(row["batter"], color, size=64, display_margin=False)
            
            with cols[i]:
                st.markdown(f"""
                <div class='card' style='border-top: 3px solid {color}; text-align:center; height: 100%;'>
                    <div style='display:flex; justify-content:center; margin-bottom:6px;'>{avatar_html}</div>
                    <div style='font-weight:700; color:white; font-size:13px;'>{row["batter"]}</div>
                    <div style='font-size:10px; color:rgba(255,255,255,0.45); margin-bottom:8px;'>{team}</div>
                    <div style='font-size:20px; font-weight:800; color:{color};'>{int(row["runs"])} <span style='font-size:11px; font-weight:500; color:rgba(255,255,255,0.6);'>runs</span></div>
                    <div style='font-size:12px; color:rgba(255,255,255,0.6); margin-top:4px;'>S/R: <b>{row["sr"]}</b></div>
                    <div style='font-size:11px; color:rgba(255,255,255,0.4); margin-top:2px;'>4s/6s: <b>{int(row["fours"])}/{int(row["sixes"])}</b></div>
                </div>
                """, unsafe_allow_html=True)

    # Tab 3: Bowling Leaderboard
    with tab3:
        st.markdown("<h3 style='margin: 15px 0 10px; font-family:\"Rajdhani\", sans-serif; font-weight:700;'>Top 5 Wicket Takers</h3>", unsafe_allow_html=True)
        bowl_stats = df.groupby("bowler").agg(
            wickets=("bowler_wicket", "sum"),
            runs=("runs_total", "sum"),
            balls=("valid_ball", "sum"),
            dots=("runs_batter", lambda x: (x == 0).sum())
        ).reset_index()
        bowl_stats = bowl_stats[bowl_stats["balls"] > 0]
        bowl_stats["econ"] = (bowl_stats["runs"] / bowl_stats["balls"] * 6).round(2)
        top_bowlers = bowl_stats.sort_values("wickets", ascending=False).head(5)

        cols = st.columns(5)
        for i, (_, row) in enumerate(top_bowlers.iterrows()):
            info = get_player_info(row["bowler"])
            team = info["team"] if info else "IPL Player"
            color = TEAM_COLORS.get(team, "#FF6B6B")
            avatar_html = get_player_avatar_html(row["bowler"], color, size=64, display_margin=False)
            
            with cols[i]:
                st.markdown(f"""
                <div class='card' style='border-top: 3px solid {color}; text-align:center; height: 100%;'>
                    <div style='display:flex; justify-content:center; margin-bottom:6px;'>{avatar_html}</div>
                    <div style='font-weight:700; color:white; font-size:13px;'>{row["bowler"]}</div>
                    <div style='font-size:10px; color:rgba(255,255,255,0.45); margin-bottom:8px;'>{team}</div>
                    <div style='font-size:20px; font-weight:800; color:{color};'>{int(row["wickets"])} <span style='font-size:11px; font-weight:500; color:rgba(255,255,255,0.6);'>wkts</span></div>
                    <div style='font-size:12px; color:rgba(255,255,255,0.6); margin-top:4px;'>Econ: <b>{row["econ"]}</b></div>
                    <div style='font-size:11px; color:rgba(255,255,255,0.4); margin-top:2px;'>Dots: <b>{int(row["dots"])}</b></div>
                </div>
                """, unsafe_allow_html=True)

    # Tab 4: Team Performance Standings
    with tab4:
        st.markdown("<h3 style='margin: 15px 0 10px; font-family:\"Rajdhani\", sans-serif; font-weight:700;'>Wins by Team in Season</h3>", unsafe_allow_html=True)
        unique_matches = df.drop_duplicates("match_id")
        
        if not unique_matches.empty and "match_won_by" in unique_matches.columns:
            wins = unique_matches["match_won_by"].value_counts().reset_index()
            wins.columns = ["team", "wins"]
            wins["color"] = wins["team"].map(TEAM_COLORS).fillna("#888888")
            
            fig = go.Figure(go.Bar(
                x=wins["wins"],
                y=wins["team"],
                orientation="h",
                marker_color=wins["color"].tolist(),
                text=wins["wins"].apply(lambda x: f"{int(x)} wins"),
                textposition="outside",
            ))
            _fig(fig, f"Match Win Distribution — Season {season}",
                 xaxis_title="Wins count", yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Match result tracking is not available in the columns of this season data.")

    # Tab 5: Scoring Trend
    with tab5:
        st.markdown("<h3 style='margin: 15px 0 10px; font-family:\"Rajdhani\", sans-serif; font-weight:700;'>Scoring Rate Over-by-Over</h3>", unsafe_allow_html=True)
        
        over_runs = df.groupby("over")["runs_total"].mean().reset_index()
        over_runs["rpo"] = (over_runs["runs_total"] * 6).round(2)
        over_runs["over_num"] = over_runs["over"] + 1

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=over_runs["over_num"],
            y=over_runs["rpo"],
            mode="lines+markers",
            line=dict(color="#00FFFF", width=2.5),
            marker=dict(size=6, color="#00FFFF"),
            fill="tozeroy",
            fillcolor="rgba(0,229,255,0.08)",
            hovertemplate="Over %{x}<br>RPO: %{y}<extra></extra>"
        ))
        
        # Add shading for Powerplay, Middle, and Death overs
        fig2.add_vrect(x0=0.5, x1=6.5, fillcolor="#4ECDC4", opacity=0.08, line_width=0, annotation_text="Powerplay")
        fig2.add_vrect(x0=6.5, x1=15.5, fillcolor="#FFE66D", opacity=0.05, line_width=0, annotation_text="Middle Overs")
        fig2.add_vrect(x0=15.5, x1=20.5, fillcolor="#FF6B6B", opacity=0.08, line_width=0, annotation_text="Death Overs")
        
        _fig(fig2, f"Average Runs per Over in Season {season}",
             xaxis_title="Over", yaxis_title="Runs per Over (RPO)",
             xaxis=dict(tickmode="linear", tick0=1, dtick=1))
        
        st.plotly_chart(fig2, use_container_width=True)