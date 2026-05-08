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

def show_insights(data):
    st.markdown("<h2>The Dressing Room</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:rgba(255,255,255,0.5);margin-bottom:24px;'>"
        f"Interactive analytics · {data['match_id'].nunique():,} matches · "
        f"{len(data):,} deliveries · {data['season'].nunique()} seasons · "
        f"Data up to {data['date'].max()}</p>",
        unsafe_allow_html=True,
    )

    seasons = ["All Seasons"] + sorted(data["season"].astype(str).unique().tolist(), reverse=True)
    col_f1, col_f2 = st.columns([2,1])
    with col_f1:
        sel_season = st.selectbox("Filter by season", seasons)
    with col_f2:
        min_balls = st.slider("Min balls faced", 100, 1000, 300, step=50)

    df = data if sel_season=="All Seasons" else data[data["season"].astype(str)==sel_season]

    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "Batting Landscape","Run Evolution","Bowling Attack","Team DNA","Records"
    ])

    # ── TAB 1 ─────────────────────────────────────────────────────
    with tab1:
        st.markdown("<h3>IPL Batting Landscape</h3>", unsafe_allow_html=True)
        st.caption("Bubble size = total runs | Hover for full stats")

        balls_col = "valid_ball" if "valid_ball" in df.columns else "runs_batter"
        bat = df.groupby(["batter","batting_team"]).agg(
            runs =("runs_batter","sum"),
            balls=(balls_col,"sum"),
            sixes=("runs_batter", lambda x: (x==6).sum()),
        ).reset_index()
        bat = bat[bat["balls"]>=min_balls].copy()
        bat["sr"] = (bat["runs"]/bat["balls"]*100).round(1)
        if "player_dismissed" in df.columns:
            dis = df[df["player_dismissed"].notna()].groupby("player_dismissed").size().reset_index(name="outs")
            bat = bat.merge(dis, left_on="batter", right_on="player_dismissed", how="left").fillna({"outs":1})
            bat["avg"] = (bat["runs"]/bat["outs"]).round(1)
        else:
            bat["avg"] = (bat["runs"]/30).round(1)
        mr = df.groupby(["match_id","batter"])["runs_batter"].sum().reset_index()
        mr["is50"]  = (mr["runs_batter"]>=50).astype(int)
        mr["is100"] = (mr["runs_batter"]>=100).astype(int)
        mil = mr.groupby("batter").agg(fifties=("is50","sum"),hundreds=("is100","sum")).reset_index()
        bat = bat.merge(mil, on="batter", how="left").fillna(0)

        fig1 = px.scatter(bat, x="sr", y="avg", size="runs",
                          color="batting_team", color_discrete_map=TEAM_COLORS,
                          hover_name="batter",
                          hover_data={"runs":True,"sr":True,"avg":True,"fifties":True,"hundreds":True,"batting_team":False},
                          size_max=50,
                          labels={"sr":"Strike Rate","avg":"Average","batting_team":"Team"},
                          **BASE)
        fig1.update_traces(marker=dict(opacity=0.8,line=dict(width=0.5,color="white")))
        _fig(fig1, "Strike Rate vs Average (bubble = total runs)")
        st.plotly_chart(fig1, use_container_width=True)

        top15 = bat.sort_values("runs",ascending=False).head(15)
        fig2 = go.Figure(go.Bar(
            x=top15["runs"], y=top15["batter"], orientation="h",
            marker_color=[TEAM_COLORS.get(t,"#666") for t in top15["batting_team"]],
            text=top15["runs"].apply(lambda x: f"{int(x):,}"),
            textposition="outside",
        ))
        _fig(fig2, "Top 15 Run Scorers", xaxis_title="Runs", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 2 ─────────────────────────────────────────────────────
    with tab2:
        st.markdown("<h3>How IPL Scoring Has Evolved</h3>", unsafe_allow_html=True)
        ss = data.groupby("season").agg(
            avg_rpb=("runs_total","mean"),
            sixes  =("runs_batter", lambda x: (x==6).sum()),
            matches=("match_id","nunique"),
        ).reset_index().sort_values("season")
        ss["rpo"]       = (ss["avg_rpb"]*6).round(2)
        ss["six_per_m"] = (ss["sixes"]/ss["matches"]).round(1)

        fig3 = make_subplots(rows=2,cols=1,
                             subplot_titles=("Avg Runs per Over by Season","Sixes per Match by Season"),
                             vertical_spacing=0.15)
        fig3.add_trace(go.Scatter(
            x=ss["season"].astype(str), y=ss["rpo"],
            mode="lines+markers+text",
            text=ss["rpo"], textposition="top center",
            textfont=dict(size=9,color="#FFE66D"),
            line=dict(color="#00FFFF",width=2.5),
            fill="tozeroy", fillcolor="rgba(0,229,255,0.08)",
        ), row=1, col=1)
        fig3.add_trace(go.Bar(
            x=ss["season"].astype(str), y=ss["six_per_m"],
            marker_color="#FF6B6B",
            text=ss["six_per_m"], textposition="outside",
        ), row=2, col=1)
        fig3.update_xaxes(tickangle=45)
        _fig(fig3, height=600, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("<h3>Run Rate Heatmap by Over</h3>", unsafe_allow_html=True)
        heat = data.groupby(["season","over"])["runs_total"].mean().round(2).reset_index()
        pivot = heat.pivot(index="season", columns="over", values="runs_total").fillna(0)
        fig4 = px.imshow(pivot, color_continuous_scale="RdYlGn",
                         labels=dict(x="Over",y="Season",color="Runs/Ball"),
                         aspect="auto", **BASE)
        _fig(fig4, "Avg Runs per Ball by Season and Over")
        st.plotly_chart(fig4, use_container_width=True)

    # ── TAB 3 ─────────────────────────────────────────────────────
    with tab3:
        st.markdown("<h3>Bowling Landscape</h3>", unsafe_allow_html=True)
        bowl = df.groupby("bowler").agg(
            wickets=("bowler_wicket","sum"),
            runs   =("runs_total","sum"),
            balls  =("valid_ball","sum"),
        ).reset_index()
        bowl = bowl[bowl["balls"]>=120].copy()
        bowl["economy"]    = (bowl["runs"]/bowl["balls"]*6).round(2)
        bowl["bowling_sr"] = (bowl["balls"]/bowl["wickets"].replace(0,float("nan"))).round(1)

        fig5 = px.scatter(bowl, x="economy", y="wickets", size="balls",
                          color="economy", color_continuous_scale="RdYlGn_r",
                          hover_name="bowler",
                          hover_data={"economy":True,"wickets":True,"bowling_sr":True},
                          size_max=40,
                          labels={"economy":"Economy Rate","wickets":"Wickets"},
                          **BASE)
        fig5.add_vline(x=8.0, line_dash="dash",
                       line_color="rgba(255,255,255,0.3)",
                       annotation_text="Economy 8.0")
        _fig(fig5, "Economy vs Wickets (bubble = balls bowled)")
        st.plotly_chart(fig5, use_container_width=True)

        top_bowl = bowl.sort_values("wickets",ascending=False).head(12)
        fig6 = go.Figure(go.Bar(
            x=top_bowl["wickets"], y=top_bowl["bowler"], orientation="h",
            marker=dict(color=top_bowl["economy"], colorscale="RdYlGn_r",
                        showscale=True, colorbar=dict(title="Economy")),
            text=top_bowl["wickets"].astype(int), textposition="outside",
        ))
        _fig(fig6, "Top Wicket Takers (colour = economy)",
             xaxis_title="Wickets", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig6, use_container_width=True)

        dots = df[df["runs_batter"]==0].groupby("bowler").size().reset_index(name="dots")
        dots = dots.merge(bowl[["bowler","balls"]], on="bowler", how="left")
        dots["dot_pct"] = (dots["dots"]/dots["balls"]*100).round(1)
        dots = dots[dots["balls"]>=200].sort_values("dots",ascending=False).head(10)
        fig7 = px.bar(dots, x="bowler", y="dots",
                      color="dot_pct", color_continuous_scale="Blues",
                      text="dots", labels={"dot_pct":"Dot %"}, **BASE)
        fig7.update_layout(coloraxis_showscale=False)
        _fig(fig7, "Most Dot Balls")
        st.plotly_chart(fig7, use_container_width=True)

    # ── TAB 4 ─────────────────────────────────────────────────────
    with tab4:
        st.markdown("<h3>Team Batting DNA</h3>", unsafe_allow_html=True)
        ts = df.groupby("batting_team").agg(
            runs   =("runs_batter","sum"),
            balls  =("valid_ball","sum"),
            sixes  =("runs_batter", lambda x: (x==6).sum()),
            fours  =("runs_batter", lambda x: (x==4).sum()),
            matches=("match_id","nunique"),
        ).reset_index()
        ts["sr"]          = (ts["runs"]/ts["balls"]*100).round(1)
        ts["sixes_per_m"] = (ts["sixes"]/ts["matches"]).round(1)
        ts["fours_per_m"] = (ts["fours"]/ts["matches"]).round(1)

        fig8 = px.bar_polar(ts.sort_values("sr",ascending=False).head(10),
                            r="sr", theta="batting_team",
                            color="batting_team", color_discrete_map=TEAM_COLORS,
                            **BASE)
        _fig(fig8, "Team Strike Rates (polar)")
        st.plotly_chart(fig8, use_container_width=True)

        fig9 = px.scatter(ts, x="fours_per_m", y="sixes_per_m",
                          size="matches", color="batting_team",
                          color_discrete_map=TEAM_COLORS,
                          hover_name="batting_team", text="batting_team",
                          labels={"fours_per_m":"Fours/Match","sixes_per_m":"Sixes/Match"},
                          **BASE)
        fig9.update_traces(textposition="top center", textfont_size=9)
        _fig(fig9, "Sixes vs Fours per Match", showlegend=False)
        st.plotly_chart(fig9, use_container_width=True)

    # ── TAB 5 ─────────────────────────────────────────────────────
    with tab5:
        st.markdown("<h3>All-Time Records</h3>", unsafe_allow_html=True)
        mr2 = df.groupby(["match_id","batter","batting_team","date"])["runs_batter"].sum().reset_index()
        mr2 = mr2.sort_values("runs_batter",ascending=False).head(10)
        for i, row in enumerate(mr2.itertuples(), 1):
            tc = TEAM_COLORS.get(row.batting_team,"#00FFFF")
            st.markdown(
                f"<div class='card'>#{i} &nbsp;<b style='color:{tc};'>{row.batter}</b> &nbsp;"
                f"<span style='color:#FFE66D;font-size:20px;font-weight:800;'>{int(row.runs_batter)}</span>"
                f" runs &nbsp;|&nbsp; {row.batting_team} &nbsp;|&nbsp; {row.date}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<h3>Orange Cap by Season</h3>", unsafe_allow_html=True)
        tbs = data.groupby(["season","batter"])["runs_batter"].sum().reset_index()
        oc  = tbs.sort_values("runs_batter",ascending=False).groupby("season").head(1).sort_values("season")
        fig10 = px.bar(oc, x="season", y="runs_batter",
                       color="batter", text="batter",
                       labels={"runs_batter":"Runs","season":"Season"}, **BASE)
        fig10.update_traces(textangle=0, textposition="outside")
        _fig(fig10, "Orange Cap Winner Each Season", showlegend=False)
        st.plotly_chart(fig10, use_container_width=True)
