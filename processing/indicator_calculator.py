import pandas as pd

from models.timeframe import Timeframe
from processing.indicators import rsi, macd, moving_average
from utils import get_symbol_df


class IndicatorCalculator:
    """
    Рассчитывает технические индикаторы для каждого торгового символа.
    
    Используется как первый шаг аналитического пайплайна.
    """
    def calculate(self, df: pd.DataFrame, timeframe: Timeframe) -> dict[str, dict]:
        indicators = {}

        symbols = df["symbol"].unique()

        for symbol in symbols:
            symbol_df = get_symbol_df(symbol, df)

            indicators[symbol] = {
                "rsi": rsi(symbol_df),
                "macd": self._format_macd(macd(symbol_df)),
                "ema": moving_average(symbol_df, timeframe, "ema"),
                "sma": moving_average(symbol_df, timeframe, "sma"),
            }

        return indicators

    @staticmethod
    def _format_macd(
        macd_data: tuple[dict[str, float], dict[str, float]] | None
    ) -> dict[str, dict[str, float]] | None:
        if macd_data is None:
            return None

        prev, curr = macd_data

        return {
            "prev": prev,
            "curr": curr
        }