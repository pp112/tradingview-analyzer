import pandas as pd
from typing import Literal

from processing import IndicatorCalculator, SignalGenerator
from processing.indicators import correlation
from models.timeframe import Timeframe
from utils import sort_correlations


class IndicatorEngine:
    """
    Оркестратор аналитического пайплайна.

    Отвечает за координацию процессов:
    1. Расчёт индикаторов (IndicatorCalculator)
    2. Генерация торговых сигналов (SignalGenerator)
    3. Расчёт корреляций между активами
    """
    def __init__(
        self, 
        upper_rsi = 70,
        lower_rsi = 30,
        corr_sort_order: Literal["asc", "desc"] = "desc"
    ):
        self.indicator_calculator = IndicatorCalculator()
        self.signal_generator = SignalGenerator(upper_rsi, lower_rsi)
        self.corr_sort_order = corr_sort_order

    def process(
        self, 
        df: pd.DataFrame, 
        timeframe: Timeframe
    ) -> tuple[
        dict[str, dict], 
        list[dict], 
        list[str]
    ]:
        indicators = self.indicator_calculator.calculate(df, timeframe)
        signals = self.signal_generator.generate(indicators, timeframe)

        return indicators, signals

    def calculate_correlations(self, df: pd.DataFrame) -> dict[str, float]:
        """
        Рассчитывает корреляции всех символов относительно BTC
        и возвращает их в отсортированном виде.
        """
        ticker_corrs = {}

        symbols = df['symbol'].unique()

        for symbol in symbols:
            ticker_corrs[symbol] = correlation(df, symbol)

        return sort_correlations(ticker_corrs, self.corr_sort_order)