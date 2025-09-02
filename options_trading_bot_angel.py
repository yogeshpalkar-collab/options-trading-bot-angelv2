import datetime
import time
import pandas as pd
import streamlit as st
from smartapi import SmartConnect

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

# ==============================
# INSTRUMENTS & EXPIRIES
# ==============================
def fetch_instruments(api):
    df = pd.DataFrame(api.getInstruments("NFO"))
    return df

def get_month_expiries(instruments, symbol="NIFTY"):
    today = datetime.date.today()
    this_month = today.month
    this_year = today.year

    df = instruments[instruments["name"] == symbol].copy()
    df["expiry"] = pd.to_datetime(df["expiry"]).dt.date

    month_expiries = sorted(
        df[(pd.DatetimeIndex(df["expiry"]).month == this_month) &
           (pd.DatetimeIndex(df["expiry"]).year == this_year)]["expiry"].unique()
    )
    return month_expiries

# ==============================
# MARKET DATA
# ==============================
def get_candles(api, symbol="NIFTY"):
    params = {
        "exchange": "NSE",
        "symboltoken": "99926000",  # NIFTY spot token
        "interval": "FIVE_MINUTE",
        "fromdate": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
        "todate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    data = api.getCandleData(params)
    df = pd.DataFrame(data)
    df.columns = ["datetime", "open", "high", "low", "close", "volume"]
    df["datetime"] = pd.to_datetime(df["datetime"])
    df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
    return df

def get_ltp(api, exchange, tradingsymbol, token, paper_trade):
    if paper_trade:
        return float(100 + (datetime.datetime.now().second % 20))  # mock LTP
    return api.ltpData(exchange, tradingsymbol, token)["data"]["ltp"]

# ==============================
# INDICATORS
# ==============================
def compute_indicators(df):
    df["EMA9"] = df["close"].ewm(span=9).mean()
    df["EMA21"] = df["close"].ewm(span=21).mean()
    df["VWAP"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    df["PP"] = (df["high"] + df["low"] + df["close"]) / 3
    df["BC"] = (df["high"] + df["low"]) / 2
    df["TC"] = 2 * df["PP"] - df["BC"]

    # ATR(14)
    df["H-L"] = df["high"] - df["low"]
    df["H-C"] = abs(df["high"] - df["close"].shift())
    df["L-C"] = abs(df["low"] - df["close"].shift())
    df["TR"] = df[["H-L","H-C","L-C"]].max(axis=1)
    df["ATR"] = df["TR"].rolling(14).mean()
    return df

def check_signal(df):
    latest = df.iloc[-1]
    bias_reason = []
    if latest["EMA9"] > latest["EMA21"] and latest["EMA9"] > latest["VWAP"]:
        bias_reason.append("EMA9 > EMA21 & VWAP")
        return "GO CALL", "Bullish", ", ".join(bias_reason)
    elif latest["EMA9"] < latest["EMA21"] and latest["EMA9"] < latest["VWAP"]:
        bias_reason.append("EMA9 < EMA21 & VWAP")
        return "GO PUT", "Bearish", ", ".join(bias_reason)
    return "NO-GO", "Neutral", "No clear setup"

# ==============================
# TRADING
# ==============================
def get_atm_strike(api, symbol, paper_trade):
    spot = get_ltp(api, "NSE", symbol, "99926000", paper_trade)
    return round(spot / 50) * 50

def place_order(api, tradingsymbol, token, side, qty, paper_trade):
    if paper_trade:
        print(f"📋 PAPER TRADE: {side} {tradingsymbol} x{qty}")
        return {"orderid": f"PAPER-{int(time.time())}"}
    txn_type = "BUY" if side == "BUY" else "SELL"
    return api.placeOrder(
        variety="NORMAL",
        tradingsymbol=tradingsymbol,
        symboltoken=token,
        transactiontype=txn_type,
        exchange="NFO",
        ordertype="MARKET",
        producttype="INTRADAY",
        duration="DAY",
        price=0,
        squareoff=0,
        stoploss=0,
        quantity=qty
    )

def exit_order(api, tradingsymbol, token, side, qty, paper_trade):
    if paper_trade:
        print(f"📋 PAPER EXIT: {side} {tradingsymbol} x{qty}")
        return {"orderid": f"PAPER-EXIT-{int(time.time())}"}
    txn_type = "SELL" if side == "BUY" else "BUY"
    return api.placeOrder(
        variety="NORMAL",
        tradingsymbol=tradingsymbol,
        symboltoken=token,
        transactiontype=txn_type,
        exchange="NFO",
        ordertype="MARKET",
        producttype="INTRADAY",
        duration="DAY",
        price=0,
        squareoff=0,
        stoploss=0,
        quantity=qty
    )

def monitor_position(api, entry_price, tradingsymbol, token, side, qty, stop_loss, paper_trade):
    tsl = stop_loss
    status = "OPEN"
    while True:
        ltp = get_ltp(api, "NFO", tradingsymbol, token, paper_trade)
        if side == "BUY":
            if ltp - entry_price > TARGET:
                tsl = max(tsl, ltp - TARGET)
            if ltp >= entry_price + TARGET:
                status = "TARGET HIT"
                exit_order(api, tradingsymbol, token, side, qty, paper_trade)
                break
            elif ltp <= entry_price - stop_loss or ltp <= tsl:
                status = "SL HIT" if ltp <= entry_price - stop_loss else "TSL HIT"
                exit_order(api, tradingsymbol, token, side, qty, paper_trade)
                break
        else:  # SELL
            if entry_price - ltp > TARGET:
                tsl = min(tsl, ltp + TARGET)
            if ltp <= entry_price - TARGET:
                status = "TARGET HIT"
                exit_order(api, tradingsymbol, token, side, qty, paper_trade)
                break
            elif ltp >= entry_price + stop_loss or ltp >= tsl:
                status = "SL HIT" if ltp >= entry_price + stop_loss else "TSL HIT"
                exit_order(api, tradingsymbol, token, side, qty, paper_trade)
                break
        time.sleep(5)
    return status

# ==============================
# BOT LOGIC
# ==============================
def run_bot(api, instruments, symbol="NIFTY", expiry=None, paper_trade=True):
    trades_taken = 0
    used_strikes = set()

    while trades_taken < MAX_TRADES:
        now = datetime.datetime.now().time()
        if now >= NO_TRADE_AFTER:
            print("⏳ No trades allowed after 3PM. Exiting.")
            break

        df = get_candles(api, symbol)
        df = compute_indicators(df)
        signal, bias, reason = check_signal(df)

        if signal.startswith("GO") and expiry is not None:
            atm_strike = get_atm_strike(api, symbol, paper_trade)
            if atm_strike in used_strikes:
                print("⚠️ Already traded this strike, skipping...")
                time.sleep(60)
                continue

            option_type = "CE" if "CALL" in signal else "PE"
            row = instruments[
                (instruments["name"] == symbol) &
                (pd.to_datetime(instruments["expiry"]).dt.date == expiry) &
                (instruments["strike"] == atm_strike) &
                (instruments["optiontype"] == option_type)
            ]
            if row.empty:
                print(f"Instrument not found: {symbol} {expiry} {atm_strike}{option_type}")
                time.sleep(60)
                continue

            tradingsymbol = row["tradingsymbol"].values[0]
            token = str(row["token"].values[0])
            lot_size = int(row["lotsize"].values[0])
            qty = lot_size * LOTS_PER_TRADE
            side = "BUY" if "CALL" in signal else "SELL"

            # ATR Stop Loss
            atr = df["ATR"].iloc[-1]
            stop_loss = atr + 10

            order = place_order(api, tradingsymbol, token, side, qty, paper_trade)
            print(f"📌 Order placed: {order}")

            entry_price = get_ltp(api, "NFO", tradingsymbol, token, paper_trade)
            trades_taken += 1
            used_strikes.add(atm_strike)

            status = monitor_position(api, entry_price, tradingsymbol, token, side, qty, stop_loss, paper_trade)

            trade_log.append({
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "signal": signal,
                "bias": bias,
                "reason": reason,
                "expiry": expiry,
                "strike": atm_strike,
                "entry": entry_price,
                "SL": stop_loss,
                "target": TARGET,
                "status": status
            })

        time.sleep(60)

# ==============================
# STREAMLIT ENTRY POINT
# ==============================
def main():
    st.title("Options Trading Bot (Angel One) - NIFTY Only")

    # Master password check
    input_password = st.text_input("Enter Master Password", type="password")
    if input_password != st.secrets["MASTER_PASSWORD"]:
        st.warning("Please enter the correct master password to continue.")
        st.stop()

    # Paper/Live toggle
    trade_mode = st.radio("Select Mode", ["Paper Trading", "Live Trading"], index=0)
    paper_trade = (trade_mode == "Paper Trading")

    API_KEY = st.secrets["API_KEY"]
    CLIENT_ID = st.secrets["CLIENT_ID"]
    PASSWORD = st.secrets["PASSWORD"]
    TOTP = st.secrets["TOTP"]

    api, session = login_angel(API_KEY, CLIENT_ID, PASSWORD, TOTP)
    instruments = fetch_instruments(api)

    expiries = get_month_expiries(instruments, "NIFTY")
    expiry_choice = st.selectbox("Select Expiry", expiries, index=0 if expiries else None)

    # Bias Dashboard
    df = get_candles(api, "NIFTY")
    df = compute_indicators(df)
    signal, bias, reason = check_signal(df)
    st.subheader(f"Market Bias: {bias}")
    st.caption(f"Reason: {reason}")

    if st.button("Start Bot"):
        run_bot(api, instruments, symbol="NIFTY", expiry=expiry_choice, paper_trade=paper_trade)

    if trade_log:
        st.subheader("Today's Trades")
        st.dataframe(pd.DataFrame(trade_log))

if __name__ == "__main__":
    main()
