import streamlit as st

def show_header():

    st.markdown("""
    <style>

    /* GOOGLE FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: white;
    }

    /* SIDEBAR STYLE */
    section[data-testid="stSidebar"] {
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(12px);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* GLASS CARD */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 20px;
        margin: 12px 0;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        transition: 0.3s;
    }

    .card:hover {
        transform: translateY(-6px);
    }

    /* TITLE */
    .title {
        text-align: center;
        font-size: 48px;
        font-weight: 600;
        letter-spacing: 2px;
        color: white;
    }

    /* SUBTITLE */
    .subtitle {
        text-align:center;
        color: rgba(255,255,255,0.6);
        font-size: 16px;
    }

    </style>
    """, unsafe_allow_html=True)

    # HEADER CONTENT
    st.markdown("<div class='title'>🏏 CRICKET ANALYTICS</div>", unsafe_allow_html=True)

    st.markdown("<div class='subtitle'>Smart Insights • Performance Analytics • Data Driven</div>", unsafe_allow_html=True)

    st.markdown("<div class='subtitle'>Built by Aayush Tripathi — Cricketer turned Developer</div>", unsafe_allow_html=True)


# 🔥 FINAL FIXED BACKGROUND FUNCTION
def set_bg(image_url):
    st.markdown(f"""
    <style>

    /* BACKGROUND IMAGE (WORKS 100%) */
    [data-testid="stAppViewContainer"] {{
        background: url("{image_url}") no-repeat center center fixed;
        background-size: cover;
    }}

    /* DARK OVERLAY + BLUR */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        backdrop-filter: blur(6px);
        background: rgba(0,0,0,0.6);
        z-index: 0;
    }}

    /* KEEP CONTENT ABOVE */
    .block-container {{
        position: relative;
        z-index: 1;
    }}

    </style>
    """, unsafe_allow_html=True)