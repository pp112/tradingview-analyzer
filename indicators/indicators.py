from typing import Literal
import pandas as pd

from data.websocket_client import Timeframe
from utils import get_periods_ema_sma, get_symbol_df


def correlation(df: pd.DataFrame, symbol: str) -> float:
    df_btc = get_symbol_df("BTCUSDT.P")
    df_alt = get_symbol_df(symbol, df)
    
    df_btc["Date"] = pd.to_datetime(df_btc["Timestamp"], unit="s")
    df_alt["Date"] = pd.to_datetime(df_alt["Timestamp"], unit="s")

    df_btc.set_index("Date", inplace=True)
    df_alt.set_index("Date", inplace=True)

    merged = pd.DataFrame({
        "btc": df_btc["Close"],
        "alt": df_alt["Close"]
    }).dropna()

    corr = merged["alt"].rolling(30).corr(merged["btc"]).iloc[-1]

    return round(corr, 2)

def moving_average(
    df: pd.DataFrame,
    symbol: str,
    timeframe: Timeframe,
    ma_type: Literal["ema", "sma"]
) -> list[float]:
    df_symbol = get_symbol_df(symbol, df)
    periods = get_periods_ema_sma(timeframe)

    if ma_type == "ema":
        result = df_symbol["Close"].ewm(span=periods[0], adjust=False).mean()
    elif ma_type == "sma":
        result = df_symbol["Close"].rolling(window=periods[1]).mean()

    return result[-3:].to_list()

def macd(
    df: pd.DataFrame,
    symbol: str  
) -> tuple[
    tuple[float, float], 
    tuple[float, float]
]:
    df_symbol = get_symbol_df(symbol, df)

    ema_fast = df_symbol["Close"].ewm(span=12, adjust=False).mean()
    ema_slow = df_symbol["Close"].ewm(span=26, adjust=False).mean()

    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=9, adjust=False).mean()

    result = pd.DataFrame({
        "MACD": macd,
        "MACD_signal": signal_line
    }).dropna().tail(2)

    prev, curr = result.iloc[0], result.iloc[1]

    return prev, curr

def rsi(df: pd.DataFrame, symbol: str) -> float:
    df_symbol = get_symbol_df(symbol, df)

    delta = df_symbol["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]
    