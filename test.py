import streamlit as st
import pandas as pd
import numpy as np
import openai
import requests
import plotly.graph_objects as go
import time
import os
from datetime import datetime
def fetch_btc_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50"
    headers = {"User-Agent": "Mozilla/5.0"}  # Add headers to avoid blocking
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if not isinstance(data, list):
            st.error(f"Error fetching data: {data}")  # Print actual response
            return None
        
        df = pd.DataFrame(data, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume", "CloseTime",
                                         "QuoteAssetVolume", "NumberOfTrades", "TakerBuyBaseVolume", "TakerBuyQuoteVolume", "Ignore"])
        df = df[["Timestamp", "Open", "High", "Low", "Close", "Volume"]]
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
        df.set_index("Timestamp", inplace=True)
        df = df.astype(float)
        return df

    except Exception as e:
        st.error(f"Error parsing data: {e}")
        return None
fetch_btc_data()
