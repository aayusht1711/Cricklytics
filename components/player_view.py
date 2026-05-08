import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.analysis import player_stats, player_trend

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

def _sr_label(sr):
    if sr>=180: return "Carnage!"
    if sr>=150: return "Explosive"
    if sr>=130: return "Aggressive"
    if sr>=110: return "Steady"
    return "Anchor"

def _role(df):
    if "bat_pos" not in df.columns: return "Batter"
    avg = df["bat_pos"].mean()
    if avg<=2: return "Opener"
    if avg<=5: return "Middle Order"
    return "Finisher"

def show_player_view(data):
    st.markdown("<h2>Batter Profiles</h2>", unsafe_allow_html=True)
    player   = st.selectbox("Select Batter", sorted(data["batter"].unique()))
    runs, sr = player_stats(data, player)
    df       = data[data["batter"]==player]

    balls        = int(df["valid_ball"].sum()) if "valid_ball" in df.columns else len(df)
    fours        = int((df["runs_batter"]==4).sum())
    sixes        = int((df["runs_batter"]==6).sum())
    dots         = int((df["runs_batter"]==0).sum())
    dot_pct      = round(dots/balls*100,1) if balls>0 else 0
    boundary_pct = round((fours+sixes)/balls*100,1) if balls>0 else 0
    dismissals   = int(df["player_dismissed"].notna().sum()) if "player_dismissed" in df.columns else 0
    avg          = round(runs/dismissals,2) if dismissals>0 else int(runs)
    role         = _role(df)
    team         = df["batting_team"].value_counts().index[0] if len(df)>0 else ""
    t_color      = TEAM_COLORS.get(team,"#00FFFF")
    mr           = df.groupby("match_id")["runs_batter"].sum()
    fifties      = int(((mr>=50)&(mr<100)).sum())
    hundreds     = int((mr>=100).sum())
    best         = int(mr.max()) if len(mr)>0 else 0

    st.markdown(
        f"<div class='card'><h3 style='color:{t_color};'>{player}</h3>"
        f"<p><b>Team:</b> {team} | <b>Role:</b> {role} | <b>Style:</b> {_sr_label(sr)}</p></div>",
        unsafe_allow_html=True,
    )

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Runs", f"{int(runs):,}")
    c2.metric("Strike Rate", round(sr,2))
    c3.metric("Average", avg)
    c4.metric("Best Score", best)
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Sixes", sixes)
    c6.metric("Fours", fours)
    c7.metric("50s / 100s", f"{fifties} / {hundreds}")
    c8.metric("Dot Ball %", f"{dot_pct}%")

    # Run trend
    st.markdown("<h3>Match-by-Match Runs</h3>", unsafe_allow_html=True)
    trend = player_trend(data, player).reset_index()
    trend.columns = ["match_id","runs"]
    trend["match_num"] = range(1, len(trend)+1)
    trend["rolling"]   = trend["runs"].rolling(5, min_periods=1).mean().round(1)

    r,g,b = int(t_color[1:3],16), int(t_color[3:5],16), int(t_color[5:7],16)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=trend["match_num"], y=trend["runs"],
        mode="lines+markers",
        line=dict(color=t_color, width=2),
        marker=dict(size=5, color=t_color),
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.1)",
        hovertemplate="Match %{x}<br>Runs: %{y}<extra></extra>",
        name="Runs",
    ))
    fig1.add_trace(go.Scatter(
        x=trend["match_num"], y=trend["rolling"],
        mode="lines",
        line=dict(color="#FFE66D", width=1.5, dash="dash"),
        name="5-match avg",
    ))
    if len(trend)>0:
        pk = trend["runs"].idxmax()
        fig1.add_annotation(
            x=trend.loc[pk,"match_num"], y=trend.loc[pk,"runs"],
            text=f"Best: {int(trend.loc[pk,'runs'])}",
            showarrow=True, arrowhead=2,
            font=dict(color="#FFE66D",size=11), arrowcolor="#FFE66D",
        )
    _fig(fig1, f"{player} — Runs per Match",
         xaxis_title="Match Number", yaxis_title="Runs")
    st.plotly_chart(fig1, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<h3>Strike Rate by Phase</h3>", unsafe_allow_html=True)
        df2 = df.copy()
        df2["phase"] = pd.cut(df2["over"], bins=[-1,5,14,19],
                               labels=["Powerplay","Middle","Death"])
        phase = df2.groupby("phase", observed=True).agg(
            runs=("runs_batter","sum"), balls=("valid_ball","sum")
        ).reset_index()
        phase["sr"] = (phase["runs"]/phase["balls"]*100).fillna(0).round(1)
        fig2 = px.bar(phase, x="phase", y="sr",
                      color="phase",
                      color_discrete_sequence=["#4ECDC4","#FFE66D","#FF6B6B"],
                      text="sr", labels={"phase":"Phase","sr":"Strike Rate"},
                      **BASE)
        fig2.update_traces(textposition="outside")
        _fig(fig2, "SR by Over Phase", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("<h3>Ball Outcome Distribution</h3>", unsafe_allow_html=True)
        buckets = {"Dots":dots,"Singles":int((df["runs_batter"]==1).sum()),
                   "Twos":int((df["runs_batter"]==2).sum()),
                   "Threes":int((df["runs_batter"]==3).sum()),
                   "Fours":fours,"Sixes":sixes}
        fig3 = px.pie(names=list(buckets.keys()), values=list(buckets.values()),
                      color_discrete_sequence=["#555","#4ECDC4","#45B7D1","#96CEB4",t_color,"#FFE66D"],
                      hole=0.4, **BASE)
        fig3.update_traces(textinfo="percent+label")
        _fig(fig3, "Ball Outcome Split")
        st.plotly_chart(fig3, use_container_width=True)

    if "wicket_kind" in data.columns and "player_dismissed" in data.columns:
        dismissed = data[(data["player_dismissed"]==player) & data["wicket_kind"].notna()]
        if not dismissed.empty:
            st.markdown("<h3>How Does This Batter Get Out?</h3>", unsafe_allow_html=True)
            wkt = dismissed["wicket_kind"].value_counts().reset_index()
            wkt.columns = ["kind","count"]
            fig4 = px.bar(wkt, x="kind", y="count", color="kind",
                          color_discrete_sequence=["#FF6B6B","#FFE66D","#00FFFF","#A8E6CF","#C7CEEA","#FF8B94"],
                          text="count", labels={"kind":"Dismissal","count":"Times"}, **BASE)
            fig4.update_traces(textposition="outside")
            _fig(fig4, "Dismissal Types", showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<h3>Season-by-Season Performance</h3>", unsafe_allow_html=True)
    by_season = df.groupby("season").agg(
        runs=("runs_batter","sum"), balls=("valid_ball","sum")
    ).reset_index().sort_values("season")
    by_season["sr"] = (by_season["runs"]/by_season["balls"]*100).round(1)

    fig5 = make_subplots(specs=[[{"secondary_y":True}]])
    fig5.add_trace(go.Bar(x=by_season["season"].astype(str), y=by_season["runs"],
                          name="Runs", marker_color=t_color, opacity=0.8), secondary_y=False)
    fig5.add_trace(go.Scatter(x=by_season["season"].astype(str), y=by_season["sr"],
                              name="SR", mode="lines+markers",
                              line=dict(color="#FFE66D",width=2),
                              marker=dict(size=7)), secondary_y=True)
    _fig(fig5, f"{player} — Season by Season")
    fig5.update_yaxes(title_text="Runs", secondary_y=False)
    fig5.update_yaxes(title_text="Strike Rate", secondary_y=True)
    st.plotly_chart(fig5, use_container_width=True)
