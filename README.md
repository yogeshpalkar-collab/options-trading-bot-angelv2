# Options Trading Bot (Angel One) - NIFTY Only (Secure v3 Render Importlib Fix)

## Features
- ✅ Uses stable PyPI package (smartapi-python==1.3.0)
- ✅ Import bypass using importlib (avoids SmartApi/__init__.py error on Render/Linux)
- Clean deployment on Render
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

⚠️ Reminder: Always **Clear Build Cache** on Render before redeploying.
