import streamlit as st
import pandas as pd
import numpy as np
import openai
import requests
import plotly.graph_objects as go
import time
import os
from datetime import datetime

# Load API keys from environment variables

openai.api_key = st.secrets.get("OPENAI_API_KEY")

# Function to Fetch BTC/USD Data from Binance
def fetch_btc_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50"
    response = requests.get(url).json()

    if not isinstance(response, list):
        st.error("Error fetching data. Try again later.")
        return None

    df = pd.DataFrame(response, columns=[
        "Timestamp", "Open", "High", "Low", "Close", "Volume", "CloseTime", "QuoteAssetVolume",
        "NumberOfTrades", "TakerBuyBaseVolume", "TakerBuyQuoteVolume", "Ignore"
    ])

    df = df[["Timestamp", "Open", "High", "Low", "Close", "Volume"]]
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
    df.set_index("Timestamp", inplace=True)
    df = df.astype(float)
    return df

# Function to Compute Technical Indicators
def compute_indicators(df):
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

    # RSI Calculation
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD Calculation
    df["MACD"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

# Function to Generate Trading Strategy using OpenAI
def generate_strategy(df):
    latest_data = df.tail(30).to_string(index=False)
    prompt = (
        f"Analyze the following BTC/USD price data:\n{latest_data}\n"
        "Use SMA, EMA, RSI, and MACD to determine a trading action (Buy, Sell, Hold) with justification."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Function to Plot Candlestick Chart
def plot_candlestick_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Candlestick"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], mode="lines", name="SMA 20", line=dict(color='blue', width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA_20"], mode="lines", name="EMA 20", line=dict(color='orange', width=1)))
    fig.update_layout(title="BTC/USD Candlestick Chart", xaxis_title="Time", yaxis_title="Price (USD)", template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

# Streamlit UI
st.title("🟢 Crypto Trading AI Assistant")
st.sidebar.header("Settings")

# Auto-refresh setting
auto_refresh = st.sidebar.checkbox("Auto-refresh every minute", value=True)
alert_threshold = st.sidebar.number_input("Alert if BTC crosses (USD)", min_value=0, value=0, step=100)
disable_auto_refresh = st.sidebar.checkbox("Disable Auto-refresh", value=False)
fetch_data = st.sidebar.button("Fetch BTC/USD Data")
run_analysis = st.sidebar.button("Run LLM Analysis")

if fetch_data or (auto_refresh and not disable_auto_refresh):
    df = fetch_btc_data()
    if df is not None:
        df = compute_indicators(df)
        st.subheader("Candlestick Chart")
        plot_candlestick_chart(df)
        st.subheader("Latest Data")
        st.dataframe(df.tail(10))
        
        # Alert logic
        if alert_threshold > 0 and df["Close"].iloc[-1] > alert_threshold:
            st.sidebar.warning(f"🚨 BTC/USD crossed {alert_threshold} USD!")
        
        # Auto-refresh every 60 seconds
        if auto_refresh and not disable_auto_refresh:
            time.sleep(1)
            st.rerun()

if run_analysis:
    df = fetch_btc_data()
    if df is not None:
        df = compute_indicators(df)
        st.sidebar.success("Running LLM Analysis...")
        strategy = generate_strategy(df)
        st.subheader("Trading Strategy 🧠")
        st.write(strategy)
        
        latest_price = df["Close"].iloc[-1]
        
        if "buy" in strategy.lower():
            st.success("✅ Suggested Action: BUY")
            stop_loss = latest_price * 0.99  # 1% below
            target_price = latest_price * 1.02  # 2% above
        elif "sell" in strategy.lower():
            st.error("❌ Suggested Action: SELL")
            stop_loss = latest_price * 1.01  # 1% above
            target_price = latest_price * 0.98  # 2% below
        else:
            st.warning("🔄 Suggested Action: HOLD")
            stop_loss = None
            target_price = None
        
        if stop_loss and target_price:
            st.write(f"**Stop Loss (SL):** ${stop_loss:.2f}")
            st.write(f"**Target Price (TP):** ${target_price:.2f}")
