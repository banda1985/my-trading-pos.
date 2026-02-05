import streamlit as st
import pandas as pd
import os
import hashlib
import feedparser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection  # දත්ත සුරැකීමට මෙය අවශ්‍යයි

# Page Configuration
st.set_page_config(page_title="SignalXpress 20-Pip-Challenge", layout="wide")
st_autorefresh(interval=60000, key="datetimerefresh")

# --- 🎯 Trading Plan Data (image_22317b.png අනුව) ---
PLAN_DATA = [
    (1, 100, 0.03, 106), (2, 106, 0.04, 114), (3, 114, 0.05, 124),
    (4, 124, 0.07, 138), (5, 138, 0.09, 156), (6, 156, 0.11, 178),
    (7, 178, 0.14, 206), (8, 206, 0.19, 244), (9, 244, 0.24, 292),
    (10, 292, 0.32, 356), (11, 356, 0.41, 438), (12, 438, 0.54, 546),
    (13, 546, 0.70, 686), (14, 686, 0.91, 868), (15, 868, 1.18, 1104),
    (16, 1104, 1.54, 1412), (17, 1412, 2.00, 1812), (18, 1812, 2.60, 2332),
    (19, 2332, 3.37, 3006), (20, 3006, 4.39, 3884), (21, 3884, 5.70, 5024),
    (22, 5024, 7.41, 6506), (23, 6506, 9.64, 8434), (24, 8434, 12.53, 10940),
    (25, 10940, 16.28, 14196), (26, 14196, 21.17, 18430), (27, 18430, 27.52, 23934),
    (28, 23934, 35.78, 31090), (29, 31090, 46.51, 40392), (30, 40392, 60.46, 52484)
]

LOT_SIZES = [item[2] for item in PLAN_DATA]
TARGET_BALANCES = [item[1] for item in PLAN_DATA] + [PLAN_DATA[-1][3]]
PIPS_TARGET = 20
ADMIN_PASSWORD = "573369"

# --- 🛠️ Persistance: Google Sheets Connection ---
# සටහන: මෙය සකස් කිරීමට කලින් මම පහළින් දක්වා ඇති උපදෙස් පිළිපදින්න.
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Google Sheets සම්බන්ධතාවය තවම සකස් කර නැත. දැනට Local CSV භාවිතා වේ.")

# --- Functions ---
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def get_gold_news():
    try:
        feed = feedparser.parse("https://www.investing.com/rss/news_95.rss")
        return [f"🔸 {e.title}" for e in feed.entries if "gold" in e.title.lower() or "xau" in e.title.lower()][:4]
    except: return ["⚠️ News feed unavailable."]

# --- CSS Styling (Center Alignment & Branding Hide) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stAppToolbar"] {display: none;}
    .block-container { padding-top: 2rem; text-align: center; display: flex; flex-direction: column; align-items: center; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #eeeeee; }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 32px !important; }
    [data-testid="stMetricLabel"] { justify-content: center; }
    .welcome-text { font-family: 'Arial Black', sans-serif; color: #1E88E5; font-size: 35px; width: 100%; text-align: center; }
    .datetime-box { font-size: 16px; font-weight: bold; color: #ffffff; background-color: #1E88E5; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    .stButton>button { border-radius: 10px; height: 3.5em; font-weight: bold; width: 100% !important; }
    input { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- Top Header ---
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    if st.session_state.logged_in: st.title(f"👋 Hi, {st.session_state.user_info['Name']}!")
    else: st.markdown('<div class="welcome-text">SignalXpress 20-Pip-Challenge</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="datetime-box">⏰ {datetime.now().strftime("%A, %d %B %Y | %I:%M %p")}</div>', unsafe_allow_html=True)
    with st.expander("🔥 Gold Market News", expanded=False):
        for n in get_gold_news(): st.markdown(f'<div style="font-size:12px; text-align:left;">{n}</div>', unsafe_allow_html=True)

# Navigation
if st.session_state.logged_in:
    if st.sidebar.button("🚪 Logout Account"):
        st.session_state.logged_in = False
        st.rerun()
    menu = ["Dashboard", "Leaderboard", "Admin"]
else: menu = ["Login", "Register", "Leaderboard"]
choice = st.sidebar.selectbox("Navigate Menu", menu)

# (Login, Register සහ Dashboard logic පෙර පරිදිම පවතී)
# දත්ත සුරැකීමේදී 'conn.create' හෝ 'conn.update' භාවිතා කළ හැක.
