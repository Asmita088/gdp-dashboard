import numpy as np
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

def predict_stock(symbol="INFY.NS"):
    print(f"📥 Downloading data for {symbol}...")
    data = yf.download(symbol, start="2023-01-01", end="2025-01-01", progress=False)

    if data.empty:
        return None, None, None, ([], [])

    # Prepare features and labels
    data["Prediction"] = data["Close"].shift(-1)
    X = np.array(data[["Open", "High", "Low", "Close", "Volume"]][:-1])
    y = np.array(data["Prediction"][:-1])

    # Split and train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predicted_prices = model.predict(X_test)
    score = model.score(X_test, y_test)

    # Prediction for next day
    latest_data = data[["Open", "High", "Low", "Close", "Volume"]].iloc[-1].values.reshape(1, -1)
    latest_price = float(data["Close"].iloc[-1])
    next_day_pred = float(model.predict(latest_data)[0])

    print(f"✅ Prediction Ready for {symbol}")
    return score, latest_price, next_day_pred, (y_test, predicted_prices)
