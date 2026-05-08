import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def _sr_tag(sr):
    if sr>=180: return "Carnage!"
    if sr>=150: return "Explosive"
    if sr>=130: return "Aggressive"
    if sr>=110: return "Steady"
    return "Anchor"

def show_team_view(data):
    st.markdown("<h2>Team HQ</h2>", unsafe_allow_html=True)
    team    = st.selectbox("Select Team", sorted(data["batting_team"].unique()))
    df      = data[data["batting_team"]==team]
    t_color = TEAM_COLORS.get(team,"#00FFFF")

    runs         = int(df["runs_batter"].sum())
    balls        = int(df["valid_ball"].sum()) if "valid_ball" in df.columns else len(df)
    sr           = round(runs/balls*100,2) if balls>0 else 0
    boundaries   = int((df["runs_batter"]==4).sum())
    sixes        = int((df["runs_batter"]==6).sum())
    wickets      = int(df["player_dismissed"].notna().sum()) if "player_dismissed" in df.columns else 0
    dots         = int((df["runs_batter"]==0).sum())
    dot_pct      = round(dots/balls*100,1) if balls>0 else 0
    boundary_pct = round((boundaries+sixes)/balls*100,1) if balls>0 else 0
    matches      = df["match_id"].nunique()

    st.markdown(
        f"<div class='card'><h3 style='color:{t_color};'>{team}</h3>"
        f"<p>{_sr_tag(sr)} | {matches} matches played</p></div>",
        unsafe_allow_html=True,
    )
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Runs Plundered", f"{runs:,}")
    c2.metric("Strike Rate",    sr)
    c3.metric("Wickets Lost",   wickets)
    c4.metric("Matches",        matches)
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Sixes",        sixes)
    c6.metric("Fours",        boundaries)
    c7.metric("Boundary %",   f"{boundary_pct}%")
    c8.metric("Dot Ball %",   f"{dot_pct}%")

    tab1,tab2,tab3,tab4 = st.tabs(["Run Breakdown","Top Players","Phase Analysis","Season Trend"])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            boundary_runs = boundaries*4 + sixes*6
            running_runs  = max(runs - boundary_runs, 0)
            fig1 = px.pie(names=["Boundaries","Running"],
                          values=[boundary_runs, running_runs],
                          color_discrete_sequence=[t_color,"#333"],
                          hole=0.4, **BASE)
            fig1.update_traces(textinfo="percent+label")
            _fig(fig1, "Run Composition")
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            over_avg = df.groupby("over")["runs_total"].mean().reset_index()
            fig2 = px.bar(over_avg, x="over", y="runs_total",
                          color="runs_total",
                          color_continuous_scale=["#1a1f2a",t_color,"#FFE66D"],
                          labels={"over":"Over","runs_total":"Avg Runs"}, **BASE)
            fig2.update_layout(coloraxis_showscale=False)
            _fig(fig2, "Avg Runs per Over Slot")
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        top_bat = df.groupby("batter").agg(
            runs=("runs_batter","sum"), balls=("valid_ball","sum"),
            sixes=("runs_batter", lambda x: (x==6).sum()),
        ).reset_index()
        top_bat = top_bat[top_bat["balls"]>=50].copy()
        top_bat["sr"] = (top_bat["runs"]/top_bat["balls"]*100).round(1)
        top_bat = top_bat.sort_values("runs",ascending=False).head(10)

        fig3 = go.Figure(go.Bar(
            x=top_bat["runs"], y=top_bat["batter"],
            orientation="h", marker_color=t_color,
            text=top_bat["runs"].apply(lambda x: f"{int(x):,}"),
            textposition="outside",
            customdata=top_bat[["sr","sixes"]].values,
            hovertemplate="<b>%{y}</b><br>Runs: %{x:,}<br>SR: %{customdata[0]}<br>Sixes: %{customdata[1]}<extra></extra>",
        ))
        _fig(fig3, "Top Run Scorers", xaxis_title="Runs", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

        sr_leaders = top_bat[top_bat["balls"]>=100].sort_values("sr",ascending=False).head(8)
        fig4 = px.bar(sr_leaders, x="batter", y="sr",
                      color="sr", color_continuous_scale="RdYlGn",
                      text="sr", labels={"sr":"Strike Rate","batter":""}, **BASE)
        fig4.update_traces(textposition="outside")
        fig4.update_layout(coloraxis_showscale=False)
        _fig(fig4, "Most Aggressive Batters (SR)")
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        df2 = df.copy()
        df2["phase"] = pd.cut(df2["over"], bins=[-1,5,14,19],
                               labels=["Powerplay","Middle","Death"])
        phase_stats = df2.groupby("phase", observed=True).agg(
            runs=("runs_batter","sum"), balls=("valid_ball","sum"),
            sixes=("runs_batter", lambda x: (x==6).sum()),
        ).reset_index()
        phase_stats["sr"]  = (phase_stats["runs"]/phase_stats["balls"]*100).round(1)
        phase_stats["rpo"] = (phase_stats["runs"]/phase_stats["balls"]*6).round(2)

        fig5 = make_subplots(rows=1, cols=3,
                             subplot_titles=("Runs by Phase","SR by Phase","Sixes by Phase"))
        colors = ["#4ECDC4","#FFE66D","#FF6B6B"]
        for i, col in enumerate(["runs","sr","sixes"]):
            fig5.add_trace(go.Bar(
                x=phase_stats["phase"].astype(str), y=phase_stats[col],
                marker_color=colors, text=phase_stats[col].round(1),
                textposition="outside", showlegend=False,
            ), row=1, col=i+1)
        _fig(fig5, f"{team} — Phase Breakdown")
        st.plotly_chart(fig5, use_container_width=True)

    with tab4:
        by_season = df.groupby("season").agg(
            runs=("runs_batter","sum"), balls=("valid_ball","sum"),
            matches=("match_id","nunique"),
            sixes=("runs_batter", lambda x: (x==6).sum()),
        ).reset_index().sort_values("season")
        by_season["sr"]       = (by_season["runs"]/by_season["balls"]*100).round(1)
        by_season["runs_pm"]  = (by_season["runs"]/by_season["matches"]).round(0)
        by_season["sixes_pm"] = (by_season["sixes"]/by_season["matches"]).round(1)

        fig6 = make_subplots(specs=[[{"secondary_y":True}]])
        fig6.add_trace(go.Bar(x=by_season["season"].astype(str), y=by_season["runs_pm"],
                              name="Runs/Match", marker_color=t_color, opacity=0.8),
                       secondary_y=False)
        fig6.add_trace(go.Scatter(x=by_season["season"].astype(str), y=by_season["sr"],
                                  name="SR", mode="lines+markers",
                                  line=dict(color="#FFE66D",width=2), marker=dict(size=7)),
                       secondary_y=True)
        _fig(fig6, f"{team} — Season Trend")
        fig6.update_yaxes(title_text="Runs/Match", secondary_y=False)
        fig6.update_yaxes(title_text="Strike Rate", secondary_y=True)
        st.plotly_chart(fig6, use_container_width=True)
