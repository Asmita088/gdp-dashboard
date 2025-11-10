from flask import Flask, request, jsonify
from AI_Agent_Model import predict_stock
import sqlite3

app = Flask(__name__)

# ---------- ROUTES ----------

@app.route('/')
def home():
    return {"message": "Welcome to AI Stock Agent API!"}

# --- Register User ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "All fields are required!"}), 400

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered!"}), 400

# --- Login User ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"message": f"Welcome {username}!"}), 200
    else:
        return jsonify({"error": "Invalid username or password!"}), 401

# --- Stock Prediction ---
@app.route('/predict', methods=['GET'])
def predict():
    symbol = request.args.get('symbol', 'INFY.NS')
    score, latest, next_day, _ = predict_stock(symbol)

    if score is None:
        return jsonify({"error": "Could not fetch stock data!"}), 400

    suggestion = "BUY 📈" if next_day > latest else "SELL 📉"

    return jsonify({
        "stock": symbol,
        "accuracy": f"{score*100:.2f}%",
        "current_price": latest,
        "predicted_next_day": next_day,
        "suggestion": suggestion
    }), 200

# --- Forgot Password ---
@app.route('/forgot', methods=['POST'])
def forgot():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
    conn.commit()
    updated = c.rowcount
    conn.close()

    if updated:
        return jsonify({"message": "Password updated successfully!"}), 200
    else:
        return jsonify({"error": "Email not found!"}), 404

# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True)