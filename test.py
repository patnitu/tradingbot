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
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1&interval=minutely"
    response = requests.get(url).json()

    if "prices" not in response:
        st.error(f"Error fetching data: {response}")
        return None

    df = pd.DataFrame(response["prices"], columns=["Timestamp", "Close"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
    df.set_index("Timestamp", inplace=True)
    return df


fetch_btc_data()
