import pandas as pd

from backend.models import Timeframe
from backend.processing import indicator_service
from backend.utils import filter_by_symbol


def calculate_indicators(
    df: pd.DataFrame,
    timeframe: Timeframe
) -> dict[str, dict]:
    """
    Рассчитывает технические индикаторы для каждого торгового символа.

    Используется как первый шаг аналитического пайплайна.
    """
    indicators = {}

    symbols = df["symbol"].unique()

    for symbol in symbols:
        symbol_df = filter_by_symbol(symbol, df)

        indicator_values = {
            "rsi": indicator_service.rsi_last(symbol_df),
            "rsi_extremes": indicator_service.rsi_extremes(symbol_df, 3),
            "macd": indicator_service.macd_last(symbol_df),
            "ema": indicator_service.ema_last(symbol_df, timeframe),
            "sma": indicator_service.sma_last(symbol_df, timeframe),
            "volume": indicator_service.volume_metrics(symbol_df, timeframe)
        }

        if any(v is None for v in indicator_values.values()):
            continue

        indicators[symbol] = indicator_values

    return indicators
