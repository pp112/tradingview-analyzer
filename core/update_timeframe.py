import logging

from data.timeframe import Timeframe
from data.market_data import MarketDataClient
from analysis.indicator_engine import IndicatorEngine
from utils import load_data

logger = logging.getLogger(__name__)


class TimeframeUpdater:
    """
    Пайплайн обновления таймфрейма:
    - Обновление исторических данных
    - Расчет индикаторов и проверка сигналов
    """

    def __init__(self):
        self.market_client = MarketDataClient()
        self.indicators = IndicatorEngine()

    async def update(self, timeframe: Timeframe):
        logger.info(f"Начинаем обновление таймфрейма: {timeframe.label}")

        await self.market_client.get_all_historical_ohlc(timeframe)

        df = load_data(timeframe)
        
        if timeframe == Timeframe.H1:
            logger.info(f"Обновление значений корреляций таймфрейма: {timeframe.label}")

            self.indicators.update_correlations(df)

        logger.info(f"Обновление значений индикаторов таймфрейма: {timeframe.label}")

        self.indicators.check_signals(df, timeframe)