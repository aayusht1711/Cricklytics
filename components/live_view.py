import streamlit as st
import requests
from datetime import datetime
 
# -------------------------------------------------------
# PASTE YOUR API KEY FROM https://cricketdata.org/signup.aspx
API_KEY = "87aa45a4-7440-4407-8cc1-3ead86792206"
# -------------------------------------------------------
 
BASE_URL = "https://api.cricapi.com/v1"
 
# ── self-contained styles (no dependency on header.py) ──────────
LIVE_CSS = """
<style>
.lv-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.1);
}
.lv-card:hover { transform: translateY(-3px); transition: 0.2s; }
 
.lv-score-box {
    background: rgba(0,0,0,0.35);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 12px 0;
}
.lv-score-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.lv-score-row:last-child { border-bottom: none; }
 
.lv-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: bold;
    padding: 2px 9px;
    border-radius: 4px;
    letter-spacing: 0.5px;
}
.lv-live-dot {
    width: 8px; height: 8px;
    background: #FF4444;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    box-shadow: 0 0 6px #FF4444;
}
.lv-team { color: #00FFFF; font-size: 17px; font-weight: bold; margin: 6px 0 2px; }
.lv-vs   { color: rgba(255,255,255,0.35); font-size: 12px; margin: 0 0 6px; }
.lv-status  { color: rgba(255,255,255,0.6); font-size: 13px; margin: 6px 0 2px; }
.lv-venue   { color: rgba(255,255,255,0.35); font-size: 12px; margin: 0; }
.lv-date    { color: rgba(255,255,255,0.35); font-size: 11px; }
.lv-runs    { color: white; font-size: 18px; font-weight: bold; }
.lv-overs   { color: rgba(255,255,255,0.45); font-size: 12px; font-weight: normal; }
.lv-inning  { color: rgba(255,255,255,0.65); font-size: 13px; }
.lv-empty   { text-align:center; padding: 40px 20px; }
.lv-empty-icon { font-size: 48px; margin-bottom: 12px; }
.lv-empty-title { color: rgba(255,255,255,0.6); font-size: 18px; margin-bottom: 6px; }
.lv-empty-sub   { color: rgba(255,255,255,0.35); font-size: 13px; }
.lv-footer {
    margin-top: 28px;
    padding: 10px;
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    text-align: center;
    color: rgba(255,255,255,0.25);
    font-size: 11px;
}
.lv-section-title { color: white; font-size: 18px; font-weight: bold; margin: 16px 0 10px; }
.lv-ended-label { color: rgba(255,255,255,0.35); font-size: 11px; }
</style>
"""
 
 
@st.cache_data(ttl=30)
def fetch_current_matches():
    try:
        r = requests.get(
            f"{BASE_URL}/currentMatches",
            params={"apikey": API_KEY, "offset": 0},
            timeout=6,
        )
        d = r.json()
        if d.get("status") == "success":
            return d.get("data", []), None
        return [], d.get("reason", "API returned an error")
    except requests.exceptions.Timeout:
        return [], "Request timed out — check your internet."
    except Exception as e:
        return [], str(e)
 
 
@st.cache_data(ttl=60)
def fetch_upcoming_matches():
    try:
        r = requests.get(
            f"{BASE_URL}/matches",
            params={"apikey": API_KEY, "offset": 0},
            timeout=6,
        )
        d = r.json()
        if d.get("status") == "success":
            return d.get("data", []), None
        return [], d.get("reason", "API returned an error")
    except Exception as e:
        return [], str(e)
 
 
def _badge(match_type):
    colors = {
        "T20":  ("#00FFFF", "rgba(0,255,255,0.12)", "1px solid rgba(0,255,255,0.4)"),
        "IT20": ("#00FFFF", "rgba(0,255,255,0.12)", "1px solid rgba(0,255,255,0.4)"),
        "ODI":  ("#FFE66D", "rgba(255,230,109,0.12)", "1px solid rgba(255,230,109,0.4)"),
        "TEST": ("#FF6B6B", "rgba(255,107,107,0.12)", "1px solid rgba(255,107,107,0.4)"),
    }
    mt = match_type.upper()
    col, bg, border = colors.get(mt, ("#aaa", "rgba(170,170,170,0.1)", "1px solid rgba(170,170,170,0.3)"))
    return (f'<span class="lv-badge" style="color:{col}; background:{bg}; border:{border};">'
            f'{mt}</span>')
 
 
def _score_rows(score_list):
    if not score_list:
        return '<p style="color:rgba(255,255,255,0.4); font-size:13px; margin:0;">Score not available yet</p>'
    html = ""
    for inn in score_list:
        inning = inn.get("inning", "—")
        runs   = inn.get("r", "0")
        wkts   = inn.get("w", "0")
        overs  = inn.get("o", "0")
        html += f"""
        <div class="lv-score-row">
            <span class="lv-inning">{inning}</span>
            <span class="lv-runs">{runs}/{wkts}
                <span class="lv-overs">({overs} ov)</span>
            </span>
        </div>"""
    return html
 
 
def _format_date(date_str):
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%a, %d %b %Y")
    except Exception:
        return date_str
 
 
def show_live_view():
    # Inject self-contained CSS first
    st.markdown(LIVE_CSS, unsafe_allow_html=True)
 
    # Page title
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
        <span class="lv-live-dot"></span>
        <span style="color:white; font-size:26px; font-weight:bold;">Live Cricket Scores</span>
    </div>
    <p style="color:rgba(255,255,255,0.4); font-size:13px; margin-bottom:20px;">
        Powered by CricketData.org &nbsp;·&nbsp; Auto-refreshes every 30 seconds
    </p>
    """, unsafe_allow_html=True)
 
    # ── API key not set ─────────────────────────────────────────
    if API_KEY == "YOUR_API_KEY_HERE":
        st.markdown("""
        <div class="lv-card" style="border-color:rgba(255,107,107,0.5);">
            <p style="color:#FF6B6B; font-size:16px; font-weight:bold; margin:0 0 12px;">
                ⚠️ API Key Not Set
            </p>
            <p style="color:rgba(255,255,255,0.8); font-size:14px; line-height:1.8; margin:0;">
                1 &nbsp;→&nbsp; Go to <b>https://cricketdata.org/signup.aspx</b><br>
                2 &nbsp;→&nbsp; Sign up for free (no credit card needed)<br>
                3 &nbsp;→&nbsp; Copy your API key from the dashboard<br>
                4 &nbsp;→&nbsp; Open <code>components/live_view.py</code> and replace
                <code>YOUR_API_KEY_HERE</code> with your key<br>
                5 &nbsp;→&nbsp; Restart the app
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
 
    # ── tabs ────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["🔴 Live Now", "📅 Upcoming"])
 
    # ════════════════════════════════════════════════════════════
    # TAB 1 — LIVE NOW
    # ════════════════════════════════════════════════════════════
    with tab1:
 
        col_btn, col_time = st.columns([1, 4])
        with col_btn:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with col_time:
            st.markdown(
                f'<p style="color:rgba(255,255,255,0.3); font-size:12px; margin-top:9px;">'
                f'Last checked: {datetime.now().strftime("%I:%M:%S %p")}</p>',
                unsafe_allow_html=True,
            )
 
        matches, error = fetch_current_matches()
 
        if error:
            st.markdown(f"""
            <div class="lv-card" style="border-color:rgba(255,107,107,0.4);">
                <p style="color:#FF6B6B; margin:0;">❌ {error}</p>
            </div>""", unsafe_allow_html=True)
            return
 
        live  = [m for m in matches if m.get("matchStarted") and not m.get("matchEnded")]
        ended = [m for m in matches if m.get("matchEnded")]
 
        # ── no matches ──
        if not live and not ended:
            st.markdown("""
            <div class="lv-card lv-empty">
                <div class="lv-empty-icon">🏏</div>
                <div class="lv-empty-title">No live matches right now</div>
                <div class="lv-empty-sub">Check the Upcoming tab for next matches</div>
            </div>""", unsafe_allow_html=True)
 
        # ── live matches ──
        if live:
            st.markdown(
                f'<div class="lv-section-title">🔴 Live &nbsp;<span style="color:rgba(255,255,255,0.4); '
                f'font-size:14px; font-weight:normal;">({len(live)} match{"es" if len(live)>1 else ""})</span></div>',
                unsafe_allow_html=True,
            )
            for m in live:
                teams      = m.get("teams", [])
                team1      = teams[0] if len(teams) > 0 else "Team 1"
                team2      = teams[1] if len(teams) > 1 else "Team 2"
                match_type = m.get("matchType", "T20")
                status     = m.get("status", "")
                venue      = m.get("venue", "")
                date_str   = m.get("date", "")
                score_list = m.get("score", [])
 
                venue_html = f'<p class="lv-venue">📍 {venue}</p>' if venue else ""
 
                st.markdown(f"""
                <div class="lv-card" style="border-left:3px solid #FF4444;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="lv-live-dot"></span>
                            <span style="color:#FF4444; font-size:12px; font-weight:bold;">LIVE</span>
                            {_badge(match_type)}
                        </div>
                        <span class="lv-date">{date_str}</span>
                    </div>
                    <div class="lv-team">{team1}</div>
                    <div class="lv-vs">vs</div>
                    <div class="lv-team">{team2}</div>
                    <div class="lv-score-box">{_score_rows(score_list)}</div>
                    <p class="lv-status">📊 {status}</p>
                    {venue_html}
                </div>
                """, unsafe_allow_html=True)
 
        # ── recently ended ──
        if ended:
            st.markdown(
                '<div class="lv-section-title" style="color:rgba(255,255,255,0.55);">✅ Recently Ended</div>',
                unsafe_allow_html=True,
            )
            cols = st.columns(2)
            for i, m in enumerate(ended[:6]):
                teams      = m.get("teams", [])
                team1      = teams[0] if len(teams) > 0 else "Team 1"
                team2      = teams[1] if len(teams) > 1 else "Team 2"
                match_type = m.get("matchType", "T20")
                status     = m.get("status", "")
                score_list = m.get("score", [])
 
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="lv-card" style="border-left:3px solid rgba(255,255,255,0.15); opacity:0.85;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <span class="lv-ended-label">ENDED</span>
                            {_badge(match_type)}
                        </div>
                        <div class="lv-team" style="font-size:14px;">{team1}</div>
                        <div class="lv-vs">vs</div>
                        <div class="lv-team" style="font-size:14px;">{team2}</div>
                        <div class="lv-score-box">{_score_rows(score_list)}</div>
                        <p class="lv-status" style="font-size:12px;">{status}</p>
                    </div>
                    """, unsafe_allow_html=True)
 
    # ════════════════════════════════════════════════════════════
    # TAB 2 — UPCOMING
    # ════════════════════════════════════════════════════════════
    with tab2:
 
        upcoming_all, error2 = fetch_upcoming_matches()
 
        if error2:
            st.markdown(f"""
            <div class="lv-card" style="border-color:rgba(255,107,107,0.4);">
                <p style="color:#FF6B6B; margin:0;">❌ {error2}</p>
            </div>""", unsafe_allow_html=True)
            return
 
        upcoming = [m for m in upcoming_all if not m.get("matchStarted") and not m.get("matchEnded")]
 
        if not upcoming:
            st.markdown("""
            <div class="lv-card lv-empty">
                <div class="lv-empty-icon">📅</div>
                <div class="lv-empty-title">No upcoming matches found</div>
                <div class="lv-empty-sub">Try refreshing or check back later</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(
                f'<p style="color:rgba(255,255,255,0.4); font-size:13px; margin-bottom:12px;">'
                f'Next {min(len(upcoming), 10)} scheduled matches</p>',
                unsafe_allow_html=True,
            )
            for m in upcoming[:10]:
                teams      = m.get("teams", [])
                team1      = teams[0] if len(teams) > 0 else "TBD"
                team2      = teams[1] if len(teams) > 1 else "TBD"
                match_type = m.get("matchType", "T20")
                venue      = m.get("venue", "")
                date_str   = m.get("date", "")
 
                venue_html = f'<p class="lv-venue">📍 {venue}</p>' if venue else ""
 
                st.markdown(f"""
                <div class="lv-card" style="border-left:3px solid rgba(0,255,255,0.25);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            {_badge(match_type)}
                            <div class="lv-team" style="margin-top:8px;">{team1}</div>
                            <div class="lv-vs">vs</div>
                            <div class="lv-team">{team2}</div>
                            {venue_html}
                        </div>
                        <div style="text-align:right; flex-shrink:0; padding-left:12px;">
                            <p style="color:rgba(255,255,255,0.7); font-size:13px;
                                      font-weight:bold; margin:0;">📅 {_format_date(date_str)}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
 
    # ── footer ──────────────────────────────────────────────────
    st.markdown("""
    <div class="lv-footer">
        Data from CricketData.org &nbsp;·&nbsp; Free plan ~100 calls/day &nbsp;·&nbsp;
        Scores cached for 30 seconds
    </div>
    """, unsafe_allow_html=True)
 