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

def fetch_btc_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1&interval=minutely"
    
    try:
        response = requests.get(url)
        data = response.json()

        if "prices" not in data:
            st.error(f"Error fetching data: {data}")  # Show actual error
            return None

        df = pd.DataFrame(data["prices"], columns=["Timestamp", "Close"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
        df.set_index("Timestamp", inplace=True)
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


fetch_btc_data()
