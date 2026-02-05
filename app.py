import streamlit as st
import pandas as pd
import os
import hashlib
import feedparser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Page Configuration
st.set_page_config(page_title="SignalXpress 20-Pip-Challenge", layout="wide")

# 🔄 Auto-Refresh: තත්පර 60කට වරක් කාලය යාවත්කාලීන වේ
st_autorefresh(interval=60000, key="datetimerefresh")

# Data Files
USER_FILE = "user_credentials.csv"
TRADE_FILE = "trading_master_data.csv"
ADMIN_PASSWORD = "573369"

# 🎯 Lot Sizes (Levels 1-30) - Chart එකට අනුව
LOT_SIZES = [
    0.03, 0.04, 0.05, 0.07, 0.09, 0.11, 0.14, 0.19, 0.24, 0.32,
    0.41, 0.54, 0.70, 0.91, 1.18, 1.54, 2.00, 2.60, 3.37, 4.39,
    5.7, 7.41, 9.64, 12.53, 16.28, 21.17, 27.52, 35.78, 46.51, 60.46
]
PIPS_TARGET = 20

# --- Helper Functions ---
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def save_trade(trade_data):
    df = pd.DataFrame([trade_data])
    if not os.path.isfile(TRADE_FILE): df.to_csv(TRADE_FILE, index=False)
    else: df.to_csv(TRADE_FILE, mode='a', header=False, index=False)

def get_gold_news():
    try:
        feed = feedparser.parse("https://www.investing.com/rss/news_95.rss")
        return [f"🔸 {e.title}" for e in feed.entries if "gold" in e.title.lower()][:4]
    except: return ["⚠️ News feed unavailable."]

# --- CSS Styling ---
st.markdown("""
    <style>
    .welcome-text { font-family: 'Arial Black', sans-serif; color: #1E88E5; font-size: 35px; text-align: center; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #eeeeee; }
    .datetime-box { 
        font-size: 16px; font-weight: bold; color: #ffffff; 
        background-color: #1E88E5; padding: 10px; border-radius: 8px; text-align: center;
    }
    .stButton>button { border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- Top Header (Clock & News) ---
h_col1, h_col2 = st.columns([2, 1.2])
with h_col1:
    if st.session_state.logged_in: st.title(f"👋 Hi, {st.session_state.user_info['Name']}!")
    else: st.markdown('<div class="welcome-text">SignalXpress 20-Pip-Challenge</div>', unsafe_allow_html=True)

with h_col2:
    now = datetime.now()
    st.markdown(f'<div class="datetime-box">⏰ {now.strftime("%A, %d %B %Y | %I:%M %p")}</div>', unsafe_allow_html=True)
    with st.expander("🔥 Gold Market News", expanded=False):
        for n in get_gold_news(): st.markdown(f'<div style="font-size:11px;">{n}</div>', unsafe_allow_html=True)

# Sidebar Logic
if st.session_state.logged_in:
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    menu = ["Dashboard", "Leaderboard", "Admin"]
else: menu = ["Login", "Register", "Leaderboard"]
choice = st.sidebar.selectbox("Navigate Menu", menu)

# --- Logic for Login, Register, Admin (Same as before) ---
# ... (මෙතැන කලින් ලබා දුන් Login/Register කොටස් ඇතුළත් වේ)

# --- 📊 Main Dashboard Content ---
if choice == "Dashboard" and st.session_state.logged_in:
    u = st.session_state.user_info
    t_df = pd.read_csv(TRADE_FILE) if os.path.isfile(TRADE_FILE) else pd.DataFrame()
    u_trades = t_df[t_df['User Name'] == u['User Name']] if not t_df.empty else pd.DataFrame()
    
    if not u_trades.empty:
        init_cap = float(u_trades.iloc[0]['Initial Capital'])
        u_trades['P_Num'] = u_trades['Profit Amount'].replace('[\\$,+]', '', regex=True).astype(float)
        cur_bal = init_cap + u_trades['P_Num'].sum()
        cur_lvl = len(u_trades[u_trades['Status'] == 'WON']) + 1
    else:
        init_cap = st.sidebar.number_input("Starting Capital ($)", 100.0)
        cur_bal, cur_lvl = init_cap, 1

    # Metrics Display
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Initial", f"${init_cap:,.2f}")
    c2.metric("Balance", f"${cur_bal:,.2f}", delta=f"{cur_bal - init_cap:+.2f}")
    c3.metric("Current Level", f"Level {cur_lvl}")
    if cur_lvl <= 30:
        c_lot = LOT_SIZES[cur_lvl-1]
        c_amt = round(c_lot * PIPS_TARGET * 10, 2)
        c4.metric("Target Lot", f"{c_lot}")

        # Area Chart
        st.subheader("📈 Equity Growth")
        history = [init_cap]
        tmp = init_cap
        for p in (u_trades['P_Num'] if not u_trades.empty else []):
            tmp += p
            history.append(tmp)
        st.area_chart(pd.DataFrame(history, columns=["Balance"]))

        # Action Buttons
        st.markdown("---")
        note = st.text_input("Trade Note")
        bw, bl = st.columns(2)
        if bw.button("✅ TRADE WON", type="primary"):
            save_trade({"User Name": u['User Name'], "Initial Capital": init_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": cur_lvl, "Lot": c_lot, "Profit Amount": f"+${c_amt:,.2f}", "Status": "WON", "Note": note})
            st.rerun()
        if bl.button("❌ TRADE LOST"):
            save_trade({"User Name": u['User Name'], "Initial Capital": init_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": cur_lvl, "Lot": c_lot, "Profit Amount": f"-${c_amt:,.2f}", "Status": "LOST", "Note": note})
            st.rerun()
