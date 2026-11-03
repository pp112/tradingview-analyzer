from dataclasses import dataclass

import pandas as pd

from backend.models import Timeframe
from backend.models.signal import Direction
from backend.processing import crossovers as crossover_service 
from backend.processing import indicator_service, signal_strength
from backend.utils import filter_by_symbol


@dataclass(frozen=True)
class MacdBlock:
    bar_count: int
    latest_crossover: crossover_service.Crossover | None
    strength: float | None
    macd: float
    macd_signal: float
    valid_zero_line: bool | None = None


@dataclass(frozen=True)
class EmaSmaBlock:
    bar_count: int
    latest_crossover: crossover_service.Crossover | None
    strength: float | None
    ema: float
    sma: float


def calculate_indicators(
    df: pd.DataFrame,
    timeframe: Timeframe
) -> dict[str, dict]:
    """
    Считает индикаторы по всем символам для заданного таймфрейма.
    Используется как первый шаг аналитического пайплайна.
    """
    indicators = {}
    symbols = df["symbol"].unique()

    for symbol in symbols:
        symbol_df = filter_by_symbol(symbol, df)

        indicator_values = {
            "rsi": indicator_service.rsi_last(symbol_df),
            "macd": _macd_block(symbol_df),
            "ema_sma": _ema_sma_block(symbol_df, timeframe),
            "volume": indicator_service.volume_metrics(symbol_df, timeframe)
        }

        if any(v is None for v in indicator_values.values()):
            continue
        
        indicators[symbol] = indicator_values

    return indicators


def _macd_block(symbol_df: pd.DataFrame) -> dict | None:
    """
    Данные MACD для сигнала: кол-во баров (для подсчета актуальности),
    позиция последнего пересечения, "валидность" по правилу нулевой линии и сила.

    None — слишком мало свечей у символа.
    """
    macd_df = indicator_service.macd_series(symbol_df).dropna().reset_index(drop=True)
    if len(macd_df) < 2:
        return None

    crossovers = crossover_service.find_crossovers(macd_df["MACD"], macd_df["MACD_signal"])
    latest_crossover = crossovers[-1] if crossovers else None
    curr = macd_df.iloc[-1]

    return MacdBlock(
        bar_count=len(macd_df),
        latest_crossover=latest_crossover,
        strength=signal_strength.macd_strength(crossovers, macd_df["MACD"]),
        macd=float(curr["MACD"]),
        macd_signal=float(curr["MACD_signal"]),
        valid_zero_line=_is_valid_zero_line(macd_df, latest_crossover) if latest_crossover else None,
    )


def _is_valid_zero_line(macd_df: pd.DataFrame, crossover: crossover_service.Crossover) -> bool:
    """
    Доменное правило MACD: разворот засчитывается, только если В МОМЕНТ
    САМОГО ПЕРЕСЕЧЕНИЯ обе линии были по "правильную" сторону нуля —
    ниже нуля для UP, выше нуля для DOWN.
    """
    macd = macd_df["MACD"].iloc[crossover.index]
    signal = macd_df["MACD_signal"].iloc[crossover.index]

    if crossover.direction == Direction.UP:
        return bool(macd < 0 and signal < 0)
    if crossover.direction == Direction.DOWN:
        return bool(macd > 0 and signal > 0)
    return False


def _ema_sma_block(symbol_df: pd.DataFrame, timeframe: Timeframe) -> dict | None:
    """
    Данные EMA/SMA для сигнала: кол-во баров (для подсчета актуальности),
    позиция последнего пересечения и сила.

    None — слишком мало свечей у символа.
    """
    ema = indicator_service.ema_series(symbol_df, timeframe)
    sma = indicator_service.sma_series(symbol_df, timeframe)
    df = pd.DataFrame({"ema": ema, "sma": sma}).dropna().reset_index(drop=True)
    if len(df) < 2:
        return None

    crossovers = crossover_service.find_crossovers(df["ema"], df["sma"])
    curr = df.iloc[-1]

    return EmaSmaBlock(
        bar_count=len(df),
        latest_crossover=crossovers[-1] if crossovers else None,
        strength=signal_strength.ema_sma_strength(crossovers, df["ema"], df["sma"]),
        ema=float(curr["ema"]),
        sma=float(curr["sma"]),
    )