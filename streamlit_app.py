import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from AI_Agent_Model import predict_stock

# -------------------- DATABASE FUNCTIONS --------------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        email TEXT,
        password TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(username, email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    conn.close()
    return True

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = c.fetchone()
    conn.close()
    return data

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="AI Agent - Stock Prediction", layout="wide")
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# -------------------- LOGIN / REGISTER --------------------
if not st.session_state.logged_in:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.title("🔐 Login Page")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}! 🎉")
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password")

    elif choice == "Register":
        st.title("📝 Register New Account")
        new_user = st.text_input("Create Username")
        new_email = st.text_input("Email")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Register"):
            try:
                add_user(new_user, new_email, new_pass)
                st.success("✅ Account created successfully! Please go to Login page.")
            except:
                st.error("⚠️ Username already exists. Try another.")

# -------------------- MAIN APP --------------------
else:
    st.sidebar.title(f"👋 Hello, {st.session_state.username}")
    st.title("🤖 AI Agent for Stock Market Prediction")

    symbol = st.text_input("Enter Stock Symbol (e.g., INFY.NS, TCS.NS, RELIANCE.NS):")

    if st.button("Predict"):
        with st.spinner("⏳ Please wait... fetching data and predicting..."):
            result = predict_stock(symbol)

            # --- Safeguard against missing data ---
            if result is None or result[0] is None:
                st.error("⚠️ No data found for that stock symbol. Try again.")
            else:
                score, latest_price, next_day_pred, data_tuple = result
                y_test, predicted_prices = data_tuple

                st.success(f"✅ Model Accuracy: **{score * 100:.2f}%**")
                st.write(f"**Current Price:** ₹{latest_price:.2f}")
                st.write(f"**Predicted Next Day Price:** ₹{next_day_pred:.2f}")

                if next_day_pred > latest_price:
                    st.success("📈 Suggestion: BUY (Price expected to increase)")
                else:
                    st.warning("📉 Suggestion: SELL (Price expected to decrease)")

                # --- Graph safely ---
                if len(y_test) > 0:
                    fig, ax = plt.subplots()
                    ax.plot(y_test, color='blue', label='Actual')
                    ax.plot(predicted_prices, color='red', linestyle='--', label='Predicted')
                    ax.set_title(f"Stock Prediction for {symbol}")
                    ax.set_xlabel("Days")
                    ax.set_ylabel("Price (₹)")
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.info("📊 Not enough data to display graph.")

    # -------------------- LOGOUT --------------------
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
