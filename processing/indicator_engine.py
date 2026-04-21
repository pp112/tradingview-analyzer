import pandas as pd

from processing import IndicatorCalculator, SignalGenerator
from models.timeframe import Timeframe
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
