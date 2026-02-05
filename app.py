import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="SignalXpress 20-Pip-Challenge", layout="wide")

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
    if not os.path.isfile(USER_FILE):
        df.to_csv(USER_FILE, index=False)
    else:
        df.to_csv(USER_FILE, mode='a', header=False, index=False)

def save_trade(trade_data):
    df = pd.DataFrame([trade_data])
    if not os.path.isfile(TRADE_FILE):
        df.to_csv(TRADE_FILE, index=False)
    else:
        df.to_csv(TRADE_FILE, mode='a', header=False, index=False)

def logout_user():
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()

# --- CSS Styling (Clock & Dashboard) ---
st.markdown("""
    <style>
    .main { text-align: center; }
    .welcome-text { font-family: 'Arial Black', sans-serif; color: #1E88E5; font-size: 40px; margin-bottom: 20px; text-align: center; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #eeeeee; }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 30px !important; }
    .stButton>button { border-radius: 10px; height: 3.5em; font-weight: bold; width: 100% !important; }
    
    /* දිනය සහ වේලාව සඳහා Styling */
    .datetime-box {
        position: absolute;
        top: -50px;
        right: 10px;
        text-align: right;
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #333333;
        font-weight: bold;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# --- Sidebar Logic ---
if st.session_state.logged_in:
    st.sidebar.title(f"👤 {st.session_state.user_info['Name']}")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout Account", key="logout_btn"):
        logout_user()
    st.sidebar.markdown("---")
    menu = ["Dashboard", "Leaderboard", "Admin"]
else:
    menu = ["Login", "Register", "Leaderboard", "Admin"]

choice = st.sidebar.selectbox("Navigate Menu", menu)

# --- 📅 Live Clock & Calendar Header ---
now = datetime.now()
date_time_str = now.strftime("%A, %B %d, %Y | %I:%M %p")
st.markdown(f'<div class="datetime-box">📅 {date_time_str}</div>', unsafe_allow_html=True)

# --- 🏆 Leaderboard ---
if choice == "Leaderboard":
    st.title("🏆 TOP TRADERS LEADERBOARD")
    if os.path.isfile(TRADE_FILE):
        df_all = pd.read_csv(TRADE_FILE)
        df_all['P_Num'] = df_all['Profit Amount'].replace('[\\$,+]', '', regex=True).astype(float)
        lb = df_all.groupby(['User Name']).agg({'Level': 'max', 'Initial Capital': 'first', 'P_Num': 'sum'}).reset_index()
        lb['Balance'] = lb['Initial Capital'] + lb['P_Num']
        st.table(lb.sort_values(by='Balance', ascending=False).head(10))

# --- 📝 Register ---
elif choice == "Register":
    st.subheader("📝 Register New Account")
    r_user = st.text_input("Username*")
    r_email = st.text_input("Email*")
    r_pass = st.text_input("Password*", type='password')
    r_name = st.text_input("Full Name*")
    r_phone = st.text_input("Phone Number*")
    if st.button("Create Account"):
        if r_user and r_pass and r_email:
            save_user({"User Name": r_user, "Password": make_hashes(r_pass), "Email": r_email, "Name": r_name, "Phone": str(r_phone)})
            st.success("Registration Successful!")

# --- 🔐 Login & Reset ---
elif choice == "Login":
    st.markdown('<div class="welcome-text">👋 Welcome to SignalXpress <br> 20-Pip-Challenge</div>', unsafe_allow_html=True)
    l_user = st.text_input("Username")
    l_pass = st.text_input("Password", type='password')
    if st.button("Login"):
        if os.path.isfile(USER_FILE):
            udf = pd.read_csv(USER_FILE)
            if not udf[(udf['User Name'] == l_user) & (udf['Password'] == make_hashes(l_pass))].empty:
                st.session_state.logged_in = True
                st.session_state.user_info = udf[udf['User Name'] == l_user].iloc[0].to_dict()
                st.rerun()
            else: st.error("Incorrect details.")

    with st.expander("Forgot Password?"):
        f_user = st.text_input("Username")
        f_email = st.text_input("Email")
        f_phone = st.text_input("Phone")
        f_new_pw = st.text_input("New Password", type='password')
        if st.button("Update"):
            if os.path.isfile(USER_FILE):
                udf = pd.read_csv(USER_FILE)
                idx = udf.index[(udf['User Name'] == f_user) & (udf['Email'] == f_email) & (udf['Phone'].astype(str) == str(f_phone))]
                if not idx.empty:
                    udf.at[idx[0], 'Password'] = make_hashes(f_new_pw)
                    udf.to_csv(USER_FILE, index=False)
                    st.success("Updated!")

# --- 📊 Dashboard ---
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
    c3.metric("Level", f"Level {cur_lvl}")
    
    if cur_lvl <= 30:
        c_lot = LOT_SIZES[cur_lvl-1]
        c_amt = round(c_lot * PIPS_TARGET * 10, 2)
        c4.metric("Target Lot", f"{c_lot}")

        # Area Chart
        st.subheader("📊 Equity Growth")
        history = [init_cap]
        tmp = init_cap
        for p in (u_trades['P_Num'] if not u_trades.empty else []):
            tmp += p
            history.append(tmp)
        st.area_chart(pd.DataFrame(history, columns=["Equity Balance"]))

        st.markdown("---")
        trade_note = st.text_input("Trade Note")
        
        bw, bl = st.columns(2)
        if bw.button("✅ TRADE WON", type="primary"):
            save_trade({"User Name": u['User Name'], "Initial Capital": init_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": cur_lvl, "Lot": c_lot, "Profit Amount": f"+${c_amt:,.2f}", "Status": "WON", "Note": trade_note if trade_note else "-"})
            st.rerun()
        if bl.button("❌ TRADE LOST"):
            save_trade({"User Name": u['User Name'], "Initial Capital": init_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": cur_lvl, "Lot": c_lot, "Profit Amount": f"-${c_amt:,.2f}", "Status": "LOST", "Note": trade_note if trade_note else "-"})
            st.rerun()

    if not u_trades.empty:
        with st.expander("📊 Trading History"):
            st.table(u_trades[["Date", "Level", "Lot", "Profit Amount", "Status", "Note"]])
            st.download_button("📥 Download CSV", u_trades.to_csv(index=False).encode('utf-8'), f"{u['User Name']}_report.csv", "text/csv")

# --- 🛠️ Admin ---
elif choice == "Admin":
    st.subheader("🛠️ Admin Master View")
    if st.sidebar.text_input("Admin Password", type='password') == ADMIN_PASSWORD:
        if os.path.isfile(TRADE_FILE):
            all_d = pd.read_csv(TRADE_FILE)
            st.dataframe(all_d)
            st.download_button("📥 Master CSV", all_d.to_csv(index=False).encode('utf-8'), "master_report.csv", "text/csv")
