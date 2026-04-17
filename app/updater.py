import logging

from models.timeframe import Timeframe
from market import MarketDataClient
from processing import IndicatorEngine
from storage.writer import (
    save_indicators,
    save_signals,
    save_correlations,
    save_report,
)

logger = logging.getLogger(__name__)


class TimeframeUpdater:
    """
    Пайплайн обновления данных для конкретного таймфрейма.

    Выполняет:
    - загрузку исторических TOHLC данных
    - расчет индикаторов и сигналов
    - расчёт корреляций (для H1)
    - сохранение результатов
    """
    def __init__(self):
        self.market_client = MarketDataClient()
        self.indicator_engine = IndicatorEngine()

    async def update(self, timeframe: Timeframe):
        """
        Выполняет полный цикл обновления данных для заданного таймфрейма.
        """
        logger.info(f"Начинаем обновление таймфрейма: {timeframe.label}")

        df = await self.market_client.get_all_historical_tohlc(timeframe)

        indicators, signals, reports = self.indicator_engine.process(df, timeframe)
        
        if timeframe == Timeframe.H1:
            correlations = self.indicator_engine.calculate_correlations(df)
            save_correlations(correlations)

            logger.info(f"Обновлены значения корреляций таймфрейма: {timeframe.label}")

        save_indicators(indicators, timeframe)
        save_signals(signals, timeframe)
        save_report(reports, timeframe)

        logger.info(f"Завершено обновление: {timeframe.label}")