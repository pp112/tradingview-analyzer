import pandas as pd

from backend.models import Timeframe
from backend.utils import filter_by_symbol


def rsi_series(symbol_df: pd.DataFrame) -> pd.Series:
    """
    Полная RSI серия (для графиков и анализа)
    """
    length = 14
    delta = symbol_df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/length, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
    

def rsi_last(symbol_df: pd.DataFrame) -> float | None:
    """
    Последнее значение RSI (для сигналов)
    """
    rsi = rsi_series(symbol_df)
    rsi = rsi.dropna()

    if rsi.empty:
        return None
    
    return round(float(rsi.iloc[-1]), 2)


def macd_series(symbol_df: pd.DataFrame) -> pd.DataFrame:
    """
    Полный MACD DataFrame: MACD, signal, histogram
    """
    ema_fast = symbol_df["close"].ewm(span=12, adjust=False).mean()
    ema_slow = symbol_df["close"].ewm(span=26, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    
    return pd.DataFrame({
        "MACD": macd_line,
        "MACD_signal": signal_line,
        "HIST": macd_line - signal_line
    })


def ema_series(symbol_df: pd.DataFrame, timeframe: Timeframe) -> pd.Series:
    """
    Полная EMA серия
    """
    period, _ = ema_sma_periods(timeframe)
    return symbol_df["close"].ewm(span=period, adjust=False).mean()


def sma_series(symbol_df: pd.DataFrame, timeframe: Timeframe) -> pd.Series:
    """
    Полная SMA серия
    """
    _, period = ema_sma_periods(timeframe)
    return symbol_df["close"].rolling(period).mean()


def volume_metrics(
    symbol_df: pd.DataFrame, 
    timeframe: Timeframe
) -> dict[str, float] | None:
    """
    Рассчитывает метрики объёма.
    """
    window = volume_window_for(timeframe)

    if len(symbol_df) < window:
        return None

    avg_volume = symbol_df["volume"].rolling(window).mean().iloc[-1]
    curr_volume = symbol_df["volume"].iloc[-1]

    if pd.isna(avg_volume) or avg_volume == 0:
        return None

    return {
        "curr": float(curr_volume),
        "avg": float(avg_volume),
        "ratio": round(float(curr_volume / avg_volume), 2)
    }


def correlation(symbol_df: pd.DataFrame, symbol: str) -> float | None:
    """
    Корреляция с BTC
    """
    df_btc = filter_by_symbol("BTC/USDT", symbol_df)
    df_alt = filter_by_symbol(symbol, symbol_df)

    df_btc["Date"] = pd.to_datetime(df_btc["timestamp"], unit="s")
    df_alt["Date"] = pd.to_datetime(df_alt["timestamp"], unit="s")

    df_btc.set_index("Date", inplace=True)
    df_alt.set_index("Date", inplace=True)

    merged = pd.DataFrame({
        "btc": df_btc["close"],
        "alt": df_alt["close"]
    }).dropna()

    if len(merged) < 30:
        return None

    corr = merged["alt"].rolling(30).corr(merged["btc"]).iloc[-1]
    if pd.isna(corr):
        return None

    return round(float(corr), 2)


def ema_sma_periods(timeframe: Timeframe) -> tuple[int, int]:
    return {
        Timeframe.M15: (9, 21),
        Timeframe.M30: (12, 50),
        Timeframe.H1: (21, 50),
        Timeframe.H4: (21, 100),
        Timeframe.D1: (50, 200)
    }[timeframe]


def volume_window_for(timeframe: Timeframe) -> int:
    return {
        Timeframe.M15: 10,
        Timeframe.M30: 15,
        Timeframe.H1: 20,
        Timeframe.H4: 30,
        Timeframe.D1: 50,
    }[timeframe]