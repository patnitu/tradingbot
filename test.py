import requests
import pandas as pd
import streamlit as st

def fetch_btc_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1"}  # Removed 'interval' to avoid errors
    
    response = requests.get(url, params=params)
    data = response.json()

    if "prices" not in data:
        st.error(f"Error fetching data: {data}")
        return None

    df = pd.DataFrame(data["prices"], columns=["Timestamp", "Close"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
    df.set_index("Timestamp", inplace=True)
    st.write("Df is {df}")
    return df

fetch_btc_data()
