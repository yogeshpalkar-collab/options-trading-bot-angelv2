# Options Trading Bot (Angel One) - NIFTY Only (Secure v3 Render Reinstall Fix)

## Features
- ✅ Uses stable PyPI package (smartapi-python==1.3.0)
- ✅ All dependencies explicitly installed: pycryptodome, pyotp, logzero, websocket-client
- ✅ Clean import: from SmartApi.smartConnect import SmartConnect
- Strategy: ATR+10 SL, TSL, Target, Max 3 trades/day, expiry dropdown, bias dashboard, trade log, master password, paper/live toggle

## Setup (Local)
1. Uninstall old SmartAPI:
   ```bash
   pip uninstall -y smartapi-python
   ```
2. Install cleanly:
   ```bash
   pip install -r requirements.txt
   ```
3. Run locally:
   ```bash
   streamlit run options_trading_bot_angel.py
   ```

## Deployment (Render)
- Build Command:
  ```bash
  pip install -r requirements.txt
  ```
- Start Command:
  ```bash
  streamlit run options_trading_bot_angel.py --server.port 10000 --server.address 0.0.0.0
  ```

⚠️ Reminder: Always **Clear Build Cache** on Render before redeploying to avoid stale package conflicts.
