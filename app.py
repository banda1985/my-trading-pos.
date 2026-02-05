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

# --- 🎯 Lot Sizes (Levels 1-30) ---
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

# --- CSS Styling (Modern & Centered) ---
st.markdown("""
    <style>
    .main { text-align: center; }
    .welcome-text {
        font-family: 'Arial Black', sans-serif;
        color: #1E88E5;
        font-size: 45px;
        text-shadow: 2px 2px 4px #cccccc;
        margin-bottom: 20px;
    }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #eeeeee; }
    [data-testid="stMetricValue"] { justify-content: center; font-size: 30px !important; }
    .stButton>button { border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; }
    .leaderboard-title { color: #FFD700; font-size: 35px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

menu = ["Leaderboard", "Login", "Register", "Admin"]
choice = st.sidebar.selectbox("Menu", menu)

# --- 🏆 Leaderboard ---
if choice == "Leaderboard":
    st.markdown('<div class="leaderboard-title">🏆 TOP TRADERS LEADERBOARD</div>', unsafe_allow_html=True)
    if os.path.isfile(TRADE_FILE):
        df_all = pd.read_csv(TRADE_FILE)
        df_all['Profit_Num'] = df_all['Profit Amount'].replace('[\\$,+]', '', regex=True).astype(float)
        leaderboard = df_all.groupby(['User Name']).agg({'Level': 'max', 'Initial Capital': 'first', 'Profit_Num': 'sum'}).reset_index()
        leaderboard['Balance'] = leaderboard['Initial Capital'] + leaderboard['Profit_Num']
        st.table(leaderboard.sort_values(by='Balance', ascending=False).head(10))

# --- 📝 Register ---
elif choice == "Register":
    st.subheader("📝 Create New Account")
    reg_user = st.text_input("User Name*")
    reg_email = st.text_input("Email*")
    reg_pass = st.text_input("Password*", type='password')
    reg_name = st.text_input("Full Name*")
    reg_phone = st.text_input("Phone Number*")
    reg_clz = st.text_input("Class ID (Optional)")
    if st.button("Register"):
        if reg_user and reg_pass and reg_email:
            save_user({"User Name": reg_user, "Password": make_hashes(reg_pass), "Email": reg_email, "Name": reg_name, "Phone": str(reg_phone), "Class ID": reg_clz})
            st.success("Registration Successful! Please Login.")

# --- 🔐 Login ---
elif choice == "Login":
    # --- ✨ ලස්සන Welcome Message එක ---
    st.markdown('<div class="welcome-text">👋 Welcome to SignalXpress <br> 20-Pip-Challenge</div>', unsafe_allow_html=True)
    
    login_user = st.text_input("User Name")
    login_pass = st.text_input("Password", type='password')
    if st.button("Login"):
        if os.path.isfile(USER_FILE):
            users_df = pd.read_csv(USER_FILE)
            hashed_pass = make_hashes(login_pass)
            user_record = users_df[(users_df['User Name'] == login_user) & (users_df['Password'] == hashed_pass)]
            if not user_record.empty:
                st.session_state.logged_in = True
                st.session_state.user_info = user_record.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Invalid Username or Password.")

    with st.expander("Forgot Password?"):
        re_email = st.text_input("Registered Email")
        re_phone = st.text_input("Registered Phone")
        new_pw = st.text_input("New Password", type='password')
        if st.button("Reset Now"):
            if os.path.isfile(USER_FILE):
                udf = pd.read_csv(USER_FILE)
                idx = udf.index[(udf['User Name'] == login_user) & (udf['Email'] == re_email) & (udf['Phone'].astype(str) == str(re_phone))]
                if not idx.empty:
                    udf.at[idx[0], 'Password'] = make_hashes(new_pw)
                    udf.to_csv(USER_FILE, index=False)
                    st.success("Password Updated!")

# --- 🛠️ Admin ---
elif choice == "Admin":
    st.subheader("🛠️ Admin Master Control")
    if st.text_input("Password", type='password') == ADMIN_PASSWORD:
        if os.path.isfile(TRADE_FILE):
            all_data = pd.read_csv(TRADE_FILE)
            st.dataframe(all_data)
            
            # --- 📥 Master CSV Download ---
            csv_all = all_data.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Master Trade Data (CSV)", data=csv_all, file_name='master_trade_report.csv', mime='text/csv')
            
            if st.button("🚨 Reset System Data"):
                os.remove(TRADE_FILE)
                st.rerun()

# --- 📊 Dashboard ---
if st.session_state.logged_in:
    u = st.session_state.user_info
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

    all_trades = pd.read_csv(TRADE_FILE) if os.path.isfile(TRADE_FILE) else pd.DataFrame()
    user_trades = all_trades[all_trades['User Name'] == u['User Name']] if not all_trades.empty else pd.DataFrame()
    
    if not user_trades.empty:
        initial_cap = float(user_trades.iloc[0]['Initial Capital'])
        user_trades['Profit_Numeric'] = user_trades['Profit Amount'].replace('[\\$,+]', '', regex=True).astype(float)
        current_bal = initial_cap + user_trades['Profit_Numeric'].sum()
        current_level = len(user_trades[user_trades['Status'] == 'WON']) + 1
    else:
        initial_cap = st.sidebar.number_input("Starting Capital ($)", min_value=1.0, value=100.0)
        current_bal, current_level = initial_cap, 1

    st.header(f"📈 Dashboard - {u['Name']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Initial", f"${initial_cap:,.2f}")
    c2.metric("Balance", f"${current_bal:,.2f}", delta=f"{current_bal - initial_cap:+.2f}")
    c3.metric("Level", f"{current_level}")
    
    if current_level <= 30:
        cur_lot = LOT_SIZES[current_level-1]
        amt = round(cur_lot * PIPS_TARGET * 10, 2)
        c4.metric("Target Lot", f"{cur_lot}")

        st.subheader("🚀 Equity Chart")
        history = [initial_cap]
        temp = initial_cap
        for p in user_trades['Profit_Numeric'] if not user_trades.empty else []:
            temp += p
            history.append(temp)
        st.line_chart(history)

        st.markdown("---")
        note = st.text_input("Trade Note")
        b1, b2 = st.columns(2)
        if b1.button("✅ TRADE WON", type="primary"):
            save_trade({"User Name": u['User Name'], "Initial Capital": initial_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": current_level, "Lot": cur_lot, "Profit Amount": f"+${amt:,.2f}", "Status": "WON", "Note": note if note else "-"})
            st.rerun()
        if b2.button("❌ TRADE LOST"):
            save_trade({"User Name": u['User Name'], "Initial Capital": initial_cap, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Level": current_level, "Lot": cur_lot, "Profit Amount": f"-${amt:,.2f}", "Status": "LOST", "Note": note if note else "-"})
            st.rerun()

    if not user_trades.empty:
        with st.expander("Trading History"):
            st.table(user_trades[["Date", "Level", "Lot", "Profit Amount", "Status", "Note"]])
            # --- 📥 Individual CSV Download ---
            csv_user = user_trades.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download My Trading Journal (CSV)", data=csv_user, file_name=f'{u["User Name"]}_trades.csv', mime='text/csv')
