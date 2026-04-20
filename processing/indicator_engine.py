import pandas as pd
from typing import Literal

from processing import IndicatorCalculator, SignalGenerator
from processing.indicator_service import IndicatorService
from models.timeframe import Timeframe
from utils import sort_correlations
from config import get_logger

logger = get_logger(__name__, "[SIGNALS]")


class IndicatorEngine:
    """
    Оркестратор аналитического пайплайна.

    Отвечает за координацию процессов:
    1. Расчёт индикаторов (IndicatorCalculator)
    2. Генерация торговых сигналов (SignalGenerator)
    3. Расчёт корреляций между активами
    """
    def __init__(self, upper_rsi = 70, lower_rsi = 30):
        self.indicator_calculator = IndicatorCalculator()
        self.signal_generator = SignalGenerator(upper_rsi, lower_rsi)

    def process(
        self,
        df: pd.DataFrame,
        timeframe: Timeframe
    ) -> tuple[
        dict[str, dict],
        list[dict[str, str]],
    ]:
        """
        Возвращает расчитанные индикаторы и сгенерированные сигналы
        """
        logger.info(f"{timeframe.label}: Расчёт индикаторов")

        indicators = self.indicator_calculator.calculate(df, timeframe)

        logger.info(f"{timeframe.label}: Генерация сигналов")

        signals = self.signal_generator.generate(indicators, timeframe)

        return indicators, signals

    def calculate_correlations(
        self,
        df: pd.DataFrame,
        sort_order: Literal["asc", "desc"] = "desc"
    ) -> dict[str, float]:
        """
        Рассчитывает корреляции всех символов относительно BTC
        и возвращает их в отсортированном виде.
        """
        ticker_corrs = {}

        symbols = df['symbol'].unique()

        for symbol in symbols:
            ticker_corrs[symbol] = IndicatorService.correlation(df, symbol)

        return sort_correlations(ticker_corrs, sort_order)