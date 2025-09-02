# Options Trading Bot (Angel One) - NIFTY Only (Secure v3 Render PyPI Clean)

## Features
- ✅ Uses stable PyPI package (smartapi-python==1.3.0)
- ✅ Imports SmartConnect directly from SmartApi/smartConnect.py
- ✅ No lowercase import, no try/except, no GitHub dependency
- ✅ Clean deployment on Render (Linux safe)
- Strategy: ATR+10 SL, TSL, Target, Max 3 trades/day, expiry dropdown, bias dashboard, trade log, master password, paper/live toggle

## Setup
1. pip install -r requirements.txt
2. streamlit run options_trading_bot_angel.py

## Deployment (Render)
- Build Command:
  ```bash
  pip install -r requirements.txt
  ```
- Start Command:
  ```bash
  streamlit run options_trading_bot_angel.py --server.port 10000 --server.address 0.0.0.0
  ```

⚠️ Make sure to **Clear Build Cache** on Render before redeploying, so old versions of your bot are not reused.
