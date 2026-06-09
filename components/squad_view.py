import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

TEAM_COLORS = {
    "Mumbai Indians":"#005DA0","Chennai Super Kings":"#F7C010",
    "Royal Challengers Bengaluru":"#EC1C24","Kolkata Knight Riders":"#3A225D",
    "Rajasthan Royals":"#EA1A85","Sunrisers Hyderabad":"#F7700E",
    "Delhi Capitals":"#0078BC","Punjab Kings":"#ED1B24",
    "Gujarat Titans":"#1C4966","Lucknow Super Giants":"#A72056",
}
ROLE_COLORS = {
    "Batter":"#00FFFF","All-Rounder":"#FFE66D",
    "Bowler":"#FF6B6B","Wicket-Keeper":"#4ECDC4",
}
BASE   = dict(template="plotly_dark")
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(14,17,23,0.8)",
    font=dict(family="DM Sans, sans-serif", color="white"),
    margin=dict(l=20, r=20, t=50, b=20),
)

def _fig(fig, title="", **kw):
    fig.update_layout(title=title, **LAYOUT, **kw)
    return fig

@st.cache_data
def load_profiles():
    for path in ["player_profiles_2026.csv","data/player_profiles_2026.csv"]:
        if os.path.exists(path):
            return pd.read_csv(path)
    return pd.DataFrame()

def _get_photo_b64(photo_id):
    """Load photo from local static folder as base64."""
    if not photo_id or pd.isna(photo_id):
        return None
    try:
        pid = str(int(float(photo_id)))
    except Exception:
        pid = str(photo_id).strip()
        
    paths = [
        f"static/player_photos/{pid}.png",
        f"cricklytics/static/player_photos/{pid}.png"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None

def _avatar(name, t_color, photo_id="", size=72):
    """Return img tag with local photo or initials fallback."""
    initials = "".join([p[0] for p in str(name).split()[:2]]).upper()
    fallback = (
        f"<div style='width:{size}px;height:{size}px;border-radius:50%;"
        f"background:{t_color}22;color:{t_color};"
        f"display:flex;align-items:center;justify-content:center;"
        f"font-size:{size//3}px;font-weight:800;margin:0 auto 8px;'>"
        f"{initials}</div>"
    )
    if photo_id and not pd.isna(photo_id):
        b64 = _get_photo_b64(photo_id)
        if b64:
            return (
                f"<img src='data:image/png;base64,{b64}' "
                f"style='width:{size}px;height:{size}px;border-radius:50%;"
                f"object-fit:cover;border:2px solid {t_color};"
                f"display:block;margin:0 auto 8px;'>"
            )
    return fallback

def _player_card(player, t_color, size=72):
    rc        = ROLE_COLORS.get(player["role"],"#00FFFF")
    price_str = f"₹{player['auction_price_cr']} Cr" \
                if player["auction_price_cr"]>0 else "Retained"
    avatar    = _avatar(player["name"], t_color,
                        player.get("photo_id",""), size=size)
    return (
        f"<div style='background:rgba(255,255,255,0.04);"
        f"border:1px solid rgba(255,255,255,0.08);"
        f"border-top:3px solid {t_color};"
        f"border-radius:14px;padding:16px 12px;text-align:center;"
        f"margin-bottom:12px;'>"
        f"{avatar}"
        f"<div style='color:white;font-size:13px;font-weight:700;"
        f"margin-bottom:4px;'>{player['name']}</div>"
        f"<div style='font-size:11px;color:rgba(255,255,255,0.5);"
        f"margin-bottom:6px;'>{player.get('flag','🌍')} "
        f"{player.get('nationality','India')}</div>"
        f"<div style='background:{rc}22;color:{rc};border-radius:99px;"
        f"font-size:10px;font-weight:700;padding:2px 8px;"
        f"display:inline-block;margin-bottom:6px;'>{player['role']}</div><br>"
        f"<div style='color:#FFE66D;font-size:12px;font-weight:700;'>"
        f"{price_str}</div>"
        f"</div>"
    )

def show_squad_view(data):
    st.markdown("<h2>IPL 2026 Squad Explorer</h2>", unsafe_allow_html=True)

    profiles = load_profiles()
    if profiles.empty:
        st.error("player_profiles_2026.csv not found in project root.")
        return

    # Check if local photos exist
    p_path = "static/player_photos"
    if not os.path.exists(p_path) or len(os.listdir(p_path)) == 0:
        p_path = "cricklytics/static/player_photos"
    
    photos_exist = os.path.exists(p_path) and len(os.listdir(p_path)) > 0
    photo_count  = len(os.listdir(p_path)) if photos_exist else 0

    if not photos_exist:
        st.markdown("""
        <div class='card' style='border-color:rgba(255,230,109,0.4);'>
            <p style='color:#FFE66D;font-weight:700;margin-bottom:8px;'>
                📸 Player Photos Not Downloaded Yet
            </p>
            <p style='color:rgba(255,255,255,0.7);font-size:13px;'>
                Run this once in your terminal to download all photos:<br><br>
                <code style='background:rgba(0,0,0,0.4);padding:4px 10px;
                border-radius:6px;color:#00FFFF;'>
                python download_photos.py
                </code><br><br>
                This saves 141 player photos to <b>static/player_photos/</b>
                and they load instantly after that.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            f"<p style='color:rgba(255,255,255,0.5);margin-bottom:20px;'>"
            f"252 players · 10 teams · {photo_count} photos loaded locally · "
            f"Nationality · Auction prices</p>",
            unsafe_allow_html=True,
        )

    tab1, tab2, tab3, tab4 = st.tabs([
        "Team Squads","Auction Analysis","Overseas Players","Player Search"
    ])

    # ── TAB 1 ─────────────────────────────────────────────────────
    with tab1:
        team    = st.selectbox("Select Team", sorted(profiles["team"].unique()))
        squad   = profiles[profiles["team"]==team].copy()
        t_color = TEAM_COLORS.get(team,"#00FFFF")
        abbr    = squad["team_abbr"].iloc[0] if len(squad)>0 else ""

        total_spent = squad["auction_price_cr"].sum()
        overseas    = int(squad["is_overseas"].sum())
        top_buy     = squad.sort_values("auction_price_cr",ascending=False).iloc[0]

        st.markdown(
            f"<div class='card'>"
            f"<h3 style='color:{t_color};'>{team} ({abbr})</h3>"
            f"<p>{len(squad)} players | {overseas} overseas | "
            f"₹{total_spent:.1f} Cr total spend</p></div>",
            unsafe_allow_html=True,
        )
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Squad Size",    len(squad))
        c2.metric("Overseas",      overseas)
        c3.metric("Auction Spend", f"₹{total_spent:.1f} Cr")
        c4.metric("Top Buy",       top_buy["name"],
                  f"₹{top_buy['auction_price_cr']} Cr")

        for role in ["Batter","Wicket-Keeper","All-Rounder","Bowler"]:
            rp = squad[squad["role"]==role]
            if rp.empty: continue
            rc = ROLE_COLORS.get(role,"#00FFFF")
            st.markdown(
                f"<p style='color:{rc};font-weight:700;font-size:14px;"
                f"text-transform:uppercase;letter-spacing:1px;"
                f"margin:20px 0 10px;border-bottom:1px solid {rc}33;"
                f"padding-bottom:6px;'>{role}s ({len(rp)})</p>",
                unsafe_allow_html=True,
            )
            cols = st.columns(4)
            for i,(_, p) in enumerate(rp.iterrows()):
                with cols[i%4]:
                    st.markdown(_player_card(p, t_color), unsafe_allow_html=True)

        role_counts = squad["role"].value_counts().reset_index()
        role_counts.columns = ["role","count"]
        fig1 = px.pie(role_counts, names="role", values="count",
                      color="role", color_discrete_map=ROLE_COLORS,
                      hole=0.4, **BASE)
        fig1.update_traces(textinfo="percent+label")
        _fig(fig1, f"{team} — Squad Composition")
        st.plotly_chart(fig1, use_container_width=True)

    # ── TAB 2 ─────────────────────────────────────────────────────
    with tab2:
        st.markdown("<h3>Total Auction Spend by Team</h3>", unsafe_allow_html=True)
        ts = profiles.groupby("team")["auction_price_cr"].sum().reset_index()
        ts["color"] = ts["team"].map(TEAM_COLORS).fillna("#666")
        ts = ts.sort_values("auction_price_cr",ascending=False)
        fig2 = go.Figure(go.Bar(
            x=ts["auction_price_cr"], y=ts["team"], orientation="h",
            marker_color=ts["color"].tolist(),
            text=ts["auction_price_cr"].apply(lambda x: f"₹{x:.1f} Cr"),
            textposition="outside",
        ))
        _fig(fig2,"Total Auction Spend by Team",
             xaxis_title="Crores (₹)", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<h3>Top 20 Most Expensive Players</h3>",
                    unsafe_allow_html=True)
        top20 = profiles[profiles["auction_price_cr"]>0]\
                .sort_values("auction_price_cr",ascending=False).head(20)
        cols = st.columns(4)
        for i,(_, p) in enumerate(top20.iterrows()):
            tc = TEAM_COLORS.get(p["team"],"#00FFFF")
            with cols[i%4]:
                st.markdown(_player_card(p, tc), unsafe_allow_html=True)

        role_spend = profiles.groupby("role")["auction_price_cr"].sum().reset_index()
        fig3 = px.pie(role_spend, names="role", values="auction_price_cr",
                      color="role", color_discrete_map=ROLE_COLORS,
                      hole=0.4, **BASE)
        fig3.update_traces(
            texttemplate="%{label}<br>₹%{value:.1f}Cr",
            textinfo="percent+label"
        )
        _fig(fig3,"Auction Spend by Role")
        st.plotly_chart(fig3, use_container_width=True)

        paid = profiles[profiles["auction_price_cr"]>0].copy()
        fig4 = px.strip(paid, x="role", y="auction_price_cr",
                        color="team", color_discrete_map=TEAM_COLORS,
                        hover_name="name",
                        hover_data={"auction_price_cr":True,"nationality":True},
                        labels={"auction_price_cr":"Price (Cr)","role":"Role"},
                        **BASE)
        _fig(fig4,"Price Distribution by Role")
        st.plotly_chart(fig4, use_container_width=True)

    # ── TAB 3 ─────────────────────────────────────────────────────
    with tab3:
        ov = profiles[profiles["is_overseas"]==1].copy()
        st.markdown(f"<h3>{len(ov)} Overseas Players in IPL 2026</h3>",
                    unsafe_allow_html=True)
        nc = ov["nationality"].value_counts().reset_index()
        nc.columns = ["nationality","count"]
        fig5 = px.bar(nc, x="nationality", y="count",
                      color="count", color_continuous_scale="Viridis",
                      text="count", labels={"nationality":"Country","count":"Players"},
                      **BASE)
        fig5.update_traces(textposition="outside")
        fig5.update_layout(coloraxis_showscale=False)
        _fig(fig5,"Overseas Players by Country")
        st.plotly_chart(fig5, use_container_width=True)

        for country in sorted(ov["nationality"].unique()):
            cp   = ov[ov["nationality"]==country]
            flag = cp.iloc[0]["flag"]
            st.markdown(
                f"<p style='color:#FFE66D;font-weight:700;font-size:14px;"
                f"margin:20px 0 10px;'>{flag} {country} ({len(cp)})</p>",
                unsafe_allow_html=True,
            )
            cols = st.columns(min(4,len(cp)))
            for i,(_, p) in enumerate(cp.iterrows()):
                tc = TEAM_COLORS.get(p["team"],"#00FFFF")
                with cols[i%4]:
                    st.markdown(_player_card(p, tc), unsafe_allow_html=True)

    # ── TAB 4 ─────────────────────────────────────────────────────
    with tab4:
        st.markdown("<h3>Player Search</h3>", unsafe_allow_html=True)
        col_s,col_r,col_n = st.columns(3)
        with col_s:
            search = st.text_input("Search by name", placeholder="e.g. Kohli")
        with col_r:
            rf = st.selectbox("Role",["All"]+sorted(profiles["role"].unique()))
        with col_n:
            nf = st.selectbox("Nationality",
                              ["All"]+sorted(profiles["nationality"].unique()))

        fil = profiles.copy()
        if search: fil = fil[fil["name"].str.contains(search,case=False,na=False)]
        if rf!="All": fil = fil[fil["role"]==rf]
        if nf!="All": fil = fil[fil["nationality"]==nf]

        st.markdown(
            f"<p style='color:rgba(255,255,255,0.5);font-size:13px;"
            f"margin-bottom:12px;'>{len(fil)} players found</p>",
            unsafe_allow_html=True,
        )
        if not fil.empty:
            cols = st.columns(4)
            for i,(_, p) in enumerate(fil.iterrows()):
                tc   = TEAM_COLORS.get(p["team"],"#00FFFF")
                rc   = ROLE_COLORS.get(p["role"],"#00FFFF")
                bat  = data[data["batter"]==p["name"]]
                runs = int(bat["runs_batter"].sum()) if len(bat)>0 else 0
                bls  = int(bat["valid_ball"].sum())  if len(bat)>0 else 0
                sr   = round(runs/bls*100,1) if bls>0 else 0
                wkts = int(data[data["bowler"]==p["name"]]["bowler_wicket"].sum())
                price= f"₹{p['auction_price_cr']} Cr" \
                       if p["auction_price_cr"]>0 else "Retained"
                career = ""
                if runs>0 or wkts>0:
                    career = (f"<p style='color:rgba(255,255,255,0.4);"
                              f"font-size:10px;margin-top:4px;'>"
                              f"{runs:,} runs | {wkts} wkts</p>")
                with cols[i%4]:
                    st.markdown(
                        f"<div style='background:rgba(255,255,255,0.04);"
                        f"border:1px solid rgba(255,255,255,0.08);"
                        f"border-top:3px solid {tc};"
                        f"border-radius:14px;padding:14px 10px;"
                        f"text-align:center;margin-bottom:10px;'>"
                        f"{_avatar(p['name'],tc,p.get('photo_id',''),size=64)}"
                        f"<div style='color:white;font-size:12px;font-weight:700;"
                        f"margin-bottom:3px;'>{p['name']}</div>"
                        f"<div style='font-size:10px;color:rgba(255,255,255,0.4);"
                        f"margin-bottom:4px;'>{p.get('flag','🌍')} "
                        f"{p.get('nationality','India')}</div>"
                        f"<div style='background:{rc}22;color:{rc};"
                        f"border-radius:99px;font-size:9px;font-weight:700;"
                        f"padding:1px 6px;display:inline-block;"
                        f"margin-bottom:3px;'>{p['role']}</div><br>"
                        f"<div style='font-size:10px;color:rgba(255,255,255,0.5);'>"
                        f"{p['team']}</div>"
                        f"<div style='color:#FFE66D;font-size:11px;"
                        f"font-weight:700;'>{price}</div>"
                        f"{career}</div>",
                        unsafe_allow_html=True,
                    )