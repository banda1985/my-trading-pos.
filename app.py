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

# දත්ත ගොනු (Local CSV)
USER_FILE = "user_credentials.csv"
TRADE_FILE = "trading_master_data.csv"
ADMIN_PASSWORD = "573369"

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

# --- Functions ---
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def save_data(df, filename):
    df.to_csv(filename, index=False)

def get_gold_news():
    try:
        feed = feedparser.parse("https://www.investing.com/rss/news_95.rss")
        return [f"🔸 {e.title}" for e in feed.entries if "gold" in e.title.lower() or "xau" in e.title.lower()][:4]
    except: return ["⚠️ News feed unavailable."]

# --- CSS Styling (CENTER & HIDE BRANDING) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stAppToolbar"] {display: none;}
    .block-container { padding-top: 2rem; text-align: center; display: flex; flex-direction: column; align-items: center; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #eeeeee; }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 32px !important; }
    .welcome-text { font-family: 'Arial Black', sans-serif; color: #1E88E5; font-size: 35px; width: 100%; text-align: center; }
    .datetime-box { font-size: 16px; font-weight: bold; color: #ffffff; background-color: #1E88E5; padding: 10px; border-radius: 8px; margin-bottom: 15px; }
    .stButton>button { border-radius: 10px; height: 3.5em; font-weight: bold; width: 100% !important; }
    input { text-align: center !important; }
    [data-testid="stTable"] { margin: 0 auto; width: fit-content; }
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

# --- 📝 Register Logic ---
if choice == "Register":
    st.subheader("📝 Register New Account")
    r_user = st.text_input("Username")
    r_pass = st.text_input("Password", type='password')
    r_name = st.text_input("Full Name")
    r_email = st.text_input("Email")
    r_phone = st.text_input("Phone Number")
    if st.button("Create Account"):
        new_user = pd.DataFrame([[r_user, make_hashes(r_pass), r_name, r_email, r_phone]], columns=["User Name", "Password", "Name", "Email", "Phone"])
        if not os.path.isfile(USER_FILE): new_user.to_csv(USER_FILE, index=False)
        else: new_user.to_csv(USER_FILE, mode='a', header=False, index=False)
        st.success("Registration Successful! Please Login.")

# --- 🔐 Login Logic ---
elif choice == "Login":
    l1, l2, l3 = st.columns([1, 1.5, 1])
    with l2:
        u_log = st.text_input("Username")
        p_log = st.text_input("Password", type='password')
        if st.button("Login"):
            if os.path.isfile(USER_FILE):
                udf = pd.read_csv(USER_FILE)
                match = udf[(udf['User Name'] == u_log) & (udf['Password'] == make_hashes(p_log))]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_info = match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Invalid Username or Password")
            else: st.warning("No users registered yet.")

# --- 📊 Dashboard ---
elif choice == "Dashboard" and st.session_state.logged_in:
    u = st.session_state.user_info
    t_df = pd.read_csv(TRADE_FILE) if os.path.isfile(TRADE_FILE) else pd.DataFrame(columns=["User Name", "Initial Capital", "Date", "Level", "Lot", "Profit Amount", "Status", "Note"])
    u_trades = t_df[t_df['User Name'] == u['User Name']]
    
    if not u_trades.empty:
        init_cap = float(u_trades.iloc[0]['Initial Capital'])
        u_trades['P_Num'] = u_trades['Profit Amount'].replace('[\\$,+]', '', regex=True).astype(float)
        cur_bal = init_cap + u_trades['P_Num'].sum()
        cur_lvl = len(u_trades[u_trades['Status'] == 'WON']) + 1
    else:
        init_cap = st.sidebar.number_input("Starting Capital ($)", 100.0)
        cur_bal, cur_lvl = init_cap, 1

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Initial", f"${init_cap:,.2f}")
    m2.metric("Balance", f"${cur_bal:,.2f}", delta=f"{cur_bal - init_cap:+.2f}")
    m3.metric("Level", f"{cur_lvl}")
    if cur_lvl <= 30:
        c_lot = LOT_SIZES[cur_lvl-1]
        c_amt = round(c_lot * PIPS_TARGET * 10, 2)
        m4.metric("Target Lot", f"{c_lot}")

        # Chart
        st.markdown("---")
        actual_h = [init_cap]
        tmp = init_cap
        for p in (u_trades['P_Num'] if not u_trades.empty else []):
            tmp += p
            actual_h.append(tmp)
        st.area_chart(actual_h)

        # Actions
        st.markdown("---")
        a1, a2, a3 = st.columns([1, 2, 1])
        with a2:
            note = st.text_input("Note")
            bw, bl = st.columns(2)
            if bw.button("✅ WON", type="primary"):
                entry = pd.DataFrame([[u['User Name'], init_cap, datetime.now().strftime("%Y-%m-%d"), cur_lvl, c_lot, f"+${c_amt}", "WON", note]], columns=t_df.columns[:8])
                entry.to_csv(TRADE_FILE, mode='a', header=not os.path.exists(TRADE_FILE), index=False)
                st.rerun()
            if bl.button("❌ LOST"):
                entry = pd.DataFrame([[u['User Name'], init_cap, datetime.now().strftime("%Y-%m-%d"), cur_lvl, c_lot, f"-${c_amt}", "LOST", note]], columns=t_df.columns[:8])
                entry.to_csv(TRADE_FILE, mode='a', header=not os.path.exists(TRADE_FILE), index=False)
                st.rerun()

# --- 🏆 Leaderboard ---
elif choice == "Leaderboard":
    st.subheader("🏆 Leaderboard")
    if os.path.isfile(TRADE_FILE):
        ldf = pd.read_csv(TRADE_FILE)
        ldf['P_Num'] = ldf['Profit Amount'].replace('[\\$,+]', '', regex=True).astype(float)
        res = ldf.groupby('User Name').agg({'Level': 'max', 'P_Num': 'sum'}).reset_index()
        st.table(res.sort_values(by='P_Num', ascending=False))
    else: st.info("No data yet.")

# --- 🛠️ Admin ---
elif choice == "Admin":
    if st.sidebar.text_input("Admin Password", type='password') == ADMIN_PASSWORD:
        st.subheader("🛠️ Admin Panel")
        if os.path.isfile(TRADE_FILE): st.dataframe(pd.read_csv(TRADE_FILE))
        if os.path.isfile(USER_FILE): st.dataframe(pd.read_csv(USER_FILE))
