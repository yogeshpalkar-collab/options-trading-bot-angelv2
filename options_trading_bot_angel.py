import datetime
import time
import pandas as pd
import streamlit as st
import os

# ✅ Final correct import for Render/Linux
from SmartApi.smartConnect import SmartConnect

# ==============================
# CONFIG
# ==============================
MAX_TRADES = 3
TARGET = 10            # points (fixed target)
NO_TRADE_AFTER = datetime.time(15, 0)  # 3:00 PM
LOTS_PER_TRADE = 4     # number of lots per trade

# Trade log for today
trade_log = []

# ==============================
# LOGIN
# ==============================
def login_angel(api_key, client_id, password, totp):
    obj = SmartConnect(api_key=api_key)
    session = obj.generateSession(client_id, password, totp)
    return obj, session

# (rest of bot logic same as before: indicators, trading logic, dashboard, etc.)
