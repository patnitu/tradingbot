import streamlit as st
import pandas as pd
import numpy as np
import openai
import requests
import plotly.graph_objects as go
import time
import os
from datetime import datetime
import requests
import pandas as pd
import streamlit as st

import os

# Load API Key from Environment Variable
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")

def fetch_btc_data():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"
    headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
    params = {
        "symbol": "BTC",
        "convert": "USD",
        "interval": "1m",  # ✅ Fix: Use '1m' instead of invalid value
        "count": 50
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "data" not in data:
            st.error(f"Error fetching data: {data}")  # Show actual error
            return None

        df = pd.DataFrame(data["data"]["quotes"])
        df["Timestamp"] = pd.to_datetime(df["timestamp"])
        df["Close"] = df["quote"]["USD"]["price"]
        df.set_index("Timestamp", inplace=True)
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


fetch_btc_data()
