from typing import Literal

import pandas as pd

from models.timeframe import Timeframe
from utils import get_periods_ema_sma, get_symbol_df


def correlation(df: pd.DataFrame, symbol: str) -> float:
    """
    Рассчитывает корреляцию между BTC и указанным активом.
    """
    df_btc = get_symbol_df("BTCUSDT.P", df)
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
    symbol_df: pd.DataFrame,
    timeframe: Timeframe,
    ma_type: Literal["ema", "sma"]
) -> tuple[float, float]:
    """
    Возвращает предыдущие и текущие значения EMA или SMA.
    """
    periods = get_periods_ema_sma(timeframe)

    if ma_type == "ema":
        result = symbol_df["Close"].ewm(span=periods[0], adjust=False).mean()
    elif ma_type == "sma":
        result = symbol_df["Close"].rolling(window=periods[1]).mean()
    
    result = result.dropna()
    
    if len(result) < 2:
        return None
    
    prev = round(float(result.iloc[-2]), 2)
    curr = round(float(result.iloc[-1]), 2)

    return prev, curr

def macd(
    symbol_df: pd.DataFrame,
) -> tuple[
    tuple[float, float], 
    tuple[float, float]
]:
    """
    Возвращает предыдущие и текущие значения MACD и signal line.
    """
    ema_fast = symbol_df["Close"].ewm(span=12, adjust=False).mean()
    ema_slow = symbol_df["Close"].ewm(span=26, adjust=False).mean()

    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=9, adjust=False).mean()

    macd_df = pd.DataFrame({
        "MACD": macd,
        "MACD_signal": signal_line
    }).dropna()

    if len(macd_df) < 2:
        return None, None

    prev_df, curr_df = macd_df.iloc[-2], macd_df.iloc[-1]
    
    prev = {
        "MACD": round(prev_df["MACD"], 2),
        "MACD_signal": round(prev_df["MACD_signal"], 2)
    }

    curr = {
        "MACD": round(curr_df["MACD"], 2),
        "MACD_signal": round(curr_df["MACD_signal"], 2)
    }

    return prev, curr

def rsi(symbol_df: pd.DataFrame) -> float:
    """
    Рассчитывает RSI и взвращает последнее значение.
    """
    delta = symbol_df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    value = round(rsi.iloc[-1], 2)

    return value
    