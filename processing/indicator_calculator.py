import pandas as pd

from models.timeframe import Timeframe
from processing.indicator_service import IndicatorService
from utils import filter_by_symbol


class IndicatorCalculator:
    """
    Рассчитывает технические индикаторы для каждого торгового символа.
    
    Используется как первый шаг аналитического пайплайна.
    """
    def calculate(self, df: pd.DataFrame, timeframe: Timeframe) -> dict[str, dict]:
        indicators = {}

        symbols = df["symbol"].unique()

        for symbol in symbols:
            symbol_df = filter_by_symbol(symbol, df)

            indicator_values = {
                "rsi": IndicatorService.rsi_last(symbol_df),
                "rsi_extremes": IndicatorService.rsi_extremes(symbol_df, 3),
                "macd": IndicatorService.macd_last(symbol_df),
                "ema": IndicatorService.ema_last(symbol_df, timeframe),
                "sma": IndicatorService.sma_last(symbol_df, timeframe),
                "volume": IndicatorService.volume_metrics(symbol_df, timeframe),
            }

            if any(v is None for v in indicator_values.values()):
                continue

            indicators[symbol] = indicator_values

        return indicators
