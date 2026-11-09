import pandas as pd

from backend.processing.crossovers import Crossover


# Минимум прошлых пересечений
MIN_HISTORY = 20

# Скользящее окно: сколько последних пересечений держим как историю
# для ранжирования. Ограничивает влияние старого режима волатильности.
WINDOW = 40


def macd_strength(crossovers: list[Crossover], macd_values: pd.Series) -> float | None:
    """
    Сила сигнала MACD, 0..100.
    None — истории пересечений недостаточно для перцентиля.
    """
    if len(crossovers) < MIN_HISTORY:
        return None

    gaps = [b.index - a.index for a, b in zip(crossovers[:-1], crossovers[1:])]
    extremes_values = [abs(macd_values.iloc[c.index]) for c in crossovers]

    current_gap, history_gaps = gaps[-1], gaps[-(WINDOW + 1):-1]
    current_extremes_value, history_extremes_values = extremes_values[-1], extremes_values[-(WINDOW + 1):-1]

    if len(history_gaps) < MIN_HISTORY or len(history_extremes_values) < MIN_HISTORY:
        return None

    p1 = _percentile_rank(current_gap, history_gaps)
    p2 = _percentile_rank(current_extremes_value, history_extremes_values)
    w1 = 0.45
    w2 = 0.55

    return round(_combine(p1, p2, w1, w2), 2)


def ema_sma_strength(crossovers: list[Crossover], ema_values: pd.Series, sma_values: pd.Series) -> float | None:
    """
    Сила сигнала EMA/SMA, 0..100.
    None — если истории пересечений недостаточно для перцентиля.
    """
    if len(crossovers) < MIN_HISTORY:
        return None

    gaps = [b.index - a.index for a, b in zip(crossovers[:-1], crossovers[1:])]

    spread = (ema_values - sma_values).abs()
    interval_max_spreads = [
        spread.iloc[a.index:b.index].max() 
        for a, b in zip(crossovers[:-1], crossovers[1:])
    ]

    current_gap, history_gaps = gaps[-1], gaps[-(WINDOW + 1):-1]
    current_spread, history_spreads = interval_max_spreads[-1], interval_max_spreads[-(WINDOW + 1):-1]

    if len(history_gaps) < MIN_HISTORY or len(history_spreads) < MIN_HISTORY:
        return None

    p1 = _percentile_rank(current_gap, history_gaps)
    p2 = _percentile_rank(current_spread, history_spreads)

    return round(_combine(p1, p2), 2)


def _percentile_rank(current: float, history: list[float]) -> float:
    """Процент значений в history, которые меньше current. 0..100"""
    if not history:
        return 50.0
    count = sum(1 for v in history if v <= current)
    return count * 100.0 / len(history)


def _combine(p1: float, p2: float, w1: float = 0.5, w2: float = 0.5) -> float:
    """
    Взвешенное среднее геометрическое.
    w1 и w2 — веса факторов (значимость). 
    """
    v1 = max(p1, 0.0)
    v2 = max(p2, 0.0)
    return (v1 ** w1) * (v2 ** w2)
