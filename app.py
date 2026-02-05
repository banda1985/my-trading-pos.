import streamlit as st
import pandas as pd
import os
import hashlib
import feedparser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Page Configuration
st.set_page_config(page_title="SignalXpress 20-Pip-Challenge", layout="wide")
st_autorefresh(interval=60000, key="datetimerefresh")

# දත්ත ගොනු
USER_FILE = "user_credentials.csv"
TRADE_FILE = "trading_master_data.csv"
ADMIN_PASSWORD = "573369"

# --- 🎯 Trading Plan Data (ඔයා එවපු image_22317b.png අනුව) ---
# Level, Target Starting Balance, Lot Size, Target Ending Balance
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

# --- Functions ---
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def save_trade(trade_data):
    df = pd.DataFrame([trade_data])
    if not os.path.isfile(TRADE_FILE): df.to_csv(TRADE_FILE, index=False)
    else: df.to_csv(TRADE_FILE, mode='a', header=False, index=False)

def get_gold_news():
    try:
        feed = feedparser.parse("https://www.investing.com/rss/news_95.rss")
        return [f"🔸 {e.title}" for e in feed.entries if "gold" in e.title.lower() or "xau" in e.title.lower()][:4]
    except: return ["⚠️ News feed unavailable."]

# --- CSS Styling ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stAppToolbar"] {display: none;}
    .welcome-text { font-family: 'Arial Black', sans-serif; color: #1E88E5; font-size: 35px; text-align: center; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #eeeeee; }
    .datetime-box { font-size: 16px; font-weight: bold; color: #ffffff; background-color: #1E88E5; padding: 10px; border-radius: 8px; text-align: center; }
    .stButton>button { border-radius: 10px; height: 3.5em; font-weight: bold; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- Top Header ---
h_col1, h_col2 = st.columns([2, 1.2])
with h_col1:
    if st.session_state.logged_in: st.title(f"👋 Hi, {st.session_state.user_info['Name']}!")
    else: st.markdown('<div class="welcome-text">SignalXpress 20-Pip-Challenge</div>', unsafe_allow_html=True)

with h_col2:
    st.markdown(f'<div class="datetime-box">⏰ {datetime.now().strftime("%A, %d %B %Y | %I:%M %p")}</div>', unsafe_allow_html=True)
    with st.expander("🔥 Gold Market News", expanded=False):
        for n in get_gold_news(): st.markdown(f'<div style="font-size:11px; margin-bottom:5px;">{n}</div>', unsafe_allow_html=True)

# Navigation
if st.session_state.logged_in:
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    menu = ["Dashboard", "Leaderboard", "Admin"]
else: menu = ["Login", "Register", "Leaderboard"]
choice = st.sidebar.selectbox("Navigate Menu", menu)

# --- Login Logic (Summary) ---
if choice == "Login" and not st.session_state.logged_in:
    l_user = st.text_input("Username")
    l_pass = st.text_input("Password", type='password')
    if st.button("Login"):
        if os.path.isfile(USER_FILE):
            udf = pd.read_csv(USER_FILE)
            if not udf[(udf['User Name'] == l_user) & (udf['Password'] == make_hashes(l_pass))].empty:
                st.session_state.logged_in = True
                st.session_state.user_info = udf[udf['User Name'] == l_user].iloc[0].to_dict()
                st.rerun()

# --- 📊 Dashboard Content ---
elif choice == "Dashboard" and st.session_state.logged_in:
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

    st.header(f"📈 Dashboard - {u['Name']}")
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Initial", f"${init_cap:,.2f}")
    c2.metric("Balance", f"${cur_bal:,.2f}", delta=f"{cur_bal - init_cap:+.2f}")
    c3.metric("Current Level", f"Level {cur_lvl}")
    
    if cur_lvl <= 30:
        c_lot = LOT_SIZES[cur_lvl-1]
        c_amt = round(c_lot * PIPS_TARGET * 10, 2)
        c4.metric("Target Lot", f"{c_lot}")

        # --- 📈 Target vs Actual Equity Growth ---
        st.subheader("📊 Target vs Actual Equity Growth")
        
        # Actual Data
        actual_history = [init_cap]
        tmp = init_cap
        for p in (u_trades['P_Num'] if not u_trades.empty else []):
            tmp += p
            actual_history.append(tmp)
        
        # චාර්ට් එක සඳහා දත්ත සැකසීම
        chart_len = max(len(actual_history), 5)
        plot_df = pd.DataFrame({
            "Actual Equity": actual_history + [None] * (chart_len - len(actual_history)),
            "Target Plan": TARGET_BALANCES[:chart_len]
        })
        st.line_chart(plot_df)

        st.markdown("---")
        note = st.text_input("Trade Note")
        bw, bl = st.columns(2)
        if bw.button("✅ TRADE WON", type="primary"):
            save_trade({"User Name": u['User Name'], "Initial Capital": init_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": cur_lvl, "Lot": c_lot, "Profit Amount": f"+${c_amt:,.2f}", "Status": "WON", "Note": note})
            st.rerun()
        if bl.button("❌ TRADE LOST"):
            save_trade({"User Name": u['User Name'], "Initial Capital": init_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": cur_lvl, "Lot": c_lot, "Profit Amount": f"-${c_amt:,.2f}", "Status": "LOST", "Note": note})
            st.rerun()

    # --- 📋 Plan Details Table ---
    with st.expander("📝 View Full 30-Day Plan Details"):
        plan_df = pd.DataFrame(PLAN_DATA, columns=["Level", "Start Balance", "Lot Size", "End Balance"])
        st.dataframe(plan_df, use_container_width=True)
