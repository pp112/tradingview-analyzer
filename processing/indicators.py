from typing import Literal

import pandas as pd

from models.timeframe import Timeframe
from utils import ema_sma_periods, filter_by_symbol, volume_window_for


def correlation(df: pd.DataFrame, symbol: str) -> float | None:
    """
    Рассчитывает корреляцию между BTC и указанным активом.
    """
    try:
        df_btc = filter_by_symbol("BTCUSDT.P", df)
        df_alt = filter_by_symbol(symbol, df)

        df_btc["Date"] = pd.to_datetime(df_btc["Timestamp"], unit="s")
        df_alt["Date"] = pd.to_datetime(df_alt["Timestamp"], unit="s")

        df_btc.set_index("Date", inplace=True)
        df_alt.set_index("Date", inplace=True)

        merged = pd.DataFrame({
            "btc": df_btc["Close"],
            "alt": df_alt["Close"]
        }).dropna()

        if len(merged) < 30:
            return None

        corr = merged["alt"].rolling(30).corr(merged["btc"]).iloc[-1]
        if pd.isna(corr):
            return None

        return round(float(corr), 3)
    except Exception:
        return None

def moving_average(
    symbol_df: pd.DataFrame,
    timeframe: Timeframe,
    ma_type: Literal["ema", "sma"]
) -> tuple[float, float] | None:
    """
    Возвращает предыдущие и текущие значения EMA или SMA.
    """
    try:
        ema_period, sma_period = ema_sma_periods(timeframe)

        if ma_type == "ema":
            result = symbol_df["Close"].ewm(span=ema_period, adjust=False).mean()
        elif ma_type == "sma":
            result = symbol_df["Close"].rolling(window=sma_period).mean()
        else:
            return None

        result = result.dropna()

        if len(result) < 2:
            return None

        prev = float(result.iloc[-2])
        curr = float(result.iloc[-1])

        return prev, curr
    except Exception:
        return None

def macd(
    symbol_df: pd.DataFrame,
) -> tuple[
    tuple[float, float] | None, 
    tuple[float, float] | None
]:
    """
    Возвращает предыдущие и текущие значения MACD и signal line.
    """
    try:
        ema_fast = symbol_df["Close"].ewm(span=12, adjust=False).mean()
        ema_slow = symbol_df["Close"].ewm(span=26, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=9, adjust=False).mean()

        macd_df = pd.DataFrame({
            "MACD": macd_line,
            "MACD_signal": signal_line
        }).dropna()

        if len(macd_df) < 2:
            return None, None

        prev_df, curr_df = macd_df.iloc[-2], macd_df.iloc[-1]

        prev = {
            "MACD": float(prev_df["MACD"]),
            "MACD_signal": float(prev_df["MACD_signal"])
        }

        curr = {
            "MACD": float(curr_df["MACD"]),
            "MACD_signal": float(curr_df["MACD_signal"])
        }

        return prev, curr
    except Exception:
        return None, None

def rsi(symbol_df: pd.DataFrame) -> float | None:
    """
    Рассчитывает RSI и взвращает последнее значение.
    """
    try:
        delta = symbol_df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))

        value = rsi_series.iloc[-1]
        if pd.isna(value):
            return None

        return round(float(value), 2)
    except Exception:
        return None

def volume_metrics(symbol_df: pd.DataFrame, timeframe: Timeframe) -> dict | None:
    """
    Рассчитывает метрики объёма.
    """
    window = volume_window_for(timeframe)

    if len(symbol_df) < window:
        return None

    avg_volume = symbol_df["Volume"].rolling(window).mean().iloc[-1]
    curr_volume = symbol_df["Volume"].iloc[-1]

    if pd.isna(avg_volume) or avg_volume == 0:
        return None

    return {
        "curr": float(curr_volume),
        "avg": float(avg_volume),
        "ratio": float(curr_volume / avg_volume)
    }