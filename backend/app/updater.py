from backend.models import Timeframe
from backend.market import MarketDataClient
from backend.processing import IndicatorEngine, CorrelationCalculator, PriceVolumeMonitor
from backend.storage.state_manager import StateManager
from backend.utils import read_correlations
from backend.storage.writer import (
    save_indicators,
    save_signals,
    save_correlations,
    save_market_data
)
from backend.api.api import broadcast
from backend.config import get_logger

logger = get_logger(__name__, "[UPDATER]")


class Updater:
    """
    Пайплайн обновления данных.

    Выполняет:
    - загрузку исторических данных свечей
    - расчет индикаторов и сигналов
    - расчёт корреляций (для H1)
    - сохранение результатов
    """
    def __init__(self):
        self.state_manager = StateManager()
        self.market_client = MarketDataClient()
        self.indicator_engine = IndicatorEngine()
        self.correlation_calculator = CorrelationCalculator()
        self.price_volume_monitor = PriceVolumeMonitor()

    async def update_timeframe(self, timeframe: Timeframe):
        """
        Выполняет полный цикл обновления данных для заданного таймфрейма.
        """
        logger.info(f"{timeframe.label}: Старт пайплайна")

        df_candles = await self.market_client.fetch_all_historical_candles(timeframe)

        if timeframe == Timeframe.M30:
           await self.update_price_volume(df_candles)

        if timeframe == Timeframe.H1:
            logger.info(f"{timeframe.label}: Расчет корреляций")
            correlations = self.correlation_calculator.calculate(df_candles)
            save_correlations(correlations)
        else:
            correlations = read_correlations()

        indicators, signals = self.indicator_engine.process(
            df_candles, correlations, timeframe
        )
        
        logger.info(f"{timeframe.label}: Сохранение результатов в файлы")
        
        save_signals(signals, timeframe)

        await broadcast({
            "type": "signals", 
            "timeframe": timeframe.label
        })

        save_market_data(df_candles, timeframe)
        save_indicators(indicators, timeframe)

        self.state_manager.set_updated(timeframe)

        logger.info(f"{timeframe.label}: Обновление завершено")

    async def update_price_volume(self, df):
        self.price_volume_monitor.calculate_and_save(df)
        await broadcast({"type": "price_volume"})
