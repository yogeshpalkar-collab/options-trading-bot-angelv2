# Options Trading Bot (Angel One) - NIFTY Only (Secure v3 Render)

## Features
- Trades **NIFTY only**
- Expiry dropdown (only current month expiries, nearest pre-selected)
- Dynamic lot size (pulled from Angel instruments)
- 4 lots per trade (auto-calculated from lot size)
- Stop Loss = ATR(14) + 10 points
- Trailing Stop Loss (TSL) to lock in profits
- Target = 10 points
- Max 3 trades per day
- No repeat strike
- No trades after 3 PM
- 🔘 Toggle between **Paper Trading (default)** and **Live Trading** in Streamlit UI
- 🔒 Master password protection
- 📊 Bias Dashboard (Bullish / Bearish / Neutral with reasons)
- 📑 Trade Log Table (today’s trades only)

## Setup
1. Clone or unzip this project.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add environment variables in Render or locally:
   ```bash
   MASTER_PASSWORD=your_strong_password
   API_KEY=your_api_key
   CLIENT_ID=your_client_id
   PASSWORD=your_password
   TOTP=your_totp
   ```
4. Run locally:
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
