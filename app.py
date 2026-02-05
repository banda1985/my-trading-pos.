import streamlit as st
import pandas as pd
import os
import hashlib
import feedparser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh # Auto-refresh සඳහා

# Page Configuration
st.set_page_config(page_title="SignalXpress 20-Pip-Challenge", layout="wide")

# --- 🔄 Auto-Refresh (සෑම තත්පර 60කට වරක්ම පිටුව Refresh වේ) ---
st_autorefresh(interval=60000, key="datetimerefresh")

# දත්ත ගබඩා කරන ගොනු
USER_FILE = "user_credentials.csv"
TRADE_FILE = "trading_master_data.csv"
ADMIN_PASSWORD = "573369"

# --- 🎯 Lot Sizes (Levels 1-30) - Image 22317b.png අනුව ---
LOT_SIZES = [
    0.03, 0.04, 0.05, 0.07, 0.09, 0.11, 0.14, 0.19, 0.24, 0.32,
    0.41, 0.54, 0.70, 0.91, 1.18, 1.54, 2.00, 2.60, 3.37, 4.39,
    5.7, 7.41, 9.64, 12.53, 16.28, 21.17, 27.52, 35.78, 46.51, 60.46
]
PIPS_TARGET = 20

# --- Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def save_user(user_data):
    df = pd.DataFrame([user_data])
    if not os.path.isfile(USER_FILE): df.to_csv(USER_FILE, index=False)
    else: df.to_csv(USER_FILE, mode='a', header=False, index=False)

def save_trade(trade_data):
    df = pd.DataFrame([trade_data])
    if not os.path.isfile(TRADE_FILE): df.to_csv(TRADE_FILE, index=False)
    else: df.to_csv(TRADE_FILE, mode='a', header=False, index=False)

def get_gold_news():
    try:
        feed = feedparser.parse("https://www.investing.com/rss/news_95.rss")
        gold_news = [f"🔹 {e.title}" for e in feed.entries if "gold" in e.title.lower() or "xau" in e.title.lower()]
        return gold_news[:4]
    except: return ["⚠️ පුවත් ලබා ගත නොහැක."]

# --- CSS Styling ---
st.markdown("""
    <style>
    .welcome-text { font-family: 'Arial Black', sans-serif; color: #1E88E5; font-size: 35px; text-align: center; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #eeeeee; }
    .datetime-box { 
        font-size: 16px; font-weight: bold; color: #ffffff; 
        background-color: #1E88E5; padding: 8px 15px; border-radius: 5px; 
        text-align: center; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# --- Top Header (Clock & News) ---
top_col1, top_col2 = st.columns([2, 1.2])

with top_col1:
    if st.session_state.logged_in:
        st.subheader(f"👋 Hi, {st.session_state.user_info['Name']}!")
    else:
        st.markdown('<div class="welcome-text">SignalXpress 20-Pip-Challenge</div>', unsafe_allow_html=True)

with top_col2:
    # --- 🕒 Live Auto-Updating Clock ---
    now = datetime.now()
    st.markdown(f'<div class="datetime-box">⏰ {now.strftime("%A, %d %B %Y | %I:%M %p")}</div>', unsafe_allow_html=True)
    
    # Gold News
    with st.expander("🔥 Gold Market News", expanded=True):
        for n in get_gold_news():
            st.markdown(f'<div style="font-size:11px; margin-bottom:4px;">{n}</div>', unsafe_allow_html=True)

# --- Navigation ---
if st.session_state.logged_in:
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    menu = ["Dashboard", "Leaderboard", "Admin"]
else:
    menu = ["Login", "Register", "Leaderboard"]

choice = st.sidebar.selectbox("Menu", menu)

# Dashboard & Other Logic
if choice == "Login" and not st.session_state.logged_in:
    u = st.text_input("Username")
    p = st.text_input("Password", type='password')
    if st.button("Login"):
        if os.path.isfile(USER_FILE):
            udf = pd.read_csv(USER_FILE)
            if not udf[(udf['User Name'] == u) & (udf['Password'] == make_hashes(p))].empty:
                st.session_state.logged_in = True
                st.session_state.user_info = udf[udf['User Name'] == u].iloc[0].to_dict()
                st.rerun()

elif choice == "Dashboard" and st.session_state.logged_in:
    # Metrics
    # Lot sizes and Profit Goals are based on the trading plan
    st.info("ඔබේ දත්ත සහ Chart එක මෙතැන දිස්වේවි.")
    # (Dashboard code continues here as before...)
