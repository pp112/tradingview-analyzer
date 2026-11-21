from sqlmodel import Session

from backend.events.broadcaster import Broadcaster
from backend.exchanges.base import ExchangeClient
from backend.storage.database import engine
from backend.processing.linked_indicator_values import extract_linked_indicator_values
from backend.models import Timeframe
from backend.market import MarketDataClient
from backend.processing import (
    PriceVolumeMonitor, 
    process_indicators, 
    calculate_correlations,
    check_and_auto_close,
)
from backend.app.state_manager import StateManager
from backend.utils import read_correlations
from backend.storage.writer import (
    save_indicators,
    save_linked_values,
    save_signals,
    save_correlations,
    save_market_data
)
from backend.config import get_logger

logger = get_logger(__name__, "[UPDATER]")


class Updater:
    """
    Пайплайн обновления данных.

    Выполняет:
    - загрузку исторических данных свечей
    - расчет индикаторов и сигналов
    - расчёт корреляций (для H1)
    - проверку автозакрытия
    - сохранение результатов
    """
    def __init__(
        self, 
        client: ExchangeClient, 
        broadcaster: Broadcaster,
        state_manager: StateManager,
    ):
        self.client = client
        self.broadcaster = broadcaster
        self.state_manager = state_manager
        self.market_client = MarketDataClient()
        self.price_volume_monitor = PriceVolumeMonitor()

    async def update_timeframe(self, timeframe: Timeframe):
        """
        Выполняет полный цикл обновления данных для заданного таймфрейма.
        """
        logger.info(f"{timeframe.label}: Старт пайплайна")

        df_candles = await self.market_client.fetch_all_historical_candles(timeframe)

        if df_candles.empty:
            logger.error(
                f"{timeframe.label}: исторические данные не загружены. "
                "Расчёт индикаторов остановлен."
            )
            return
        
        if timeframe == Timeframe.M30:
           await self.update_price_volume(df_candles)

        if timeframe == Timeframe.H1:
            logger.info(f"{timeframe.label}: Расчет корреляций")
            correlations = calculate_correlations(df_candles)
            save_correlations(correlations)
        else:
            correlations = read_correlations()

        indicators, signals = process_indicators(
            df_candles, correlations, timeframe
        )

        with Session(engine) as session, session.begin():
            linked_indicator_values = extract_linked_indicator_values(
                indicators, timeframe, session
            )
            await check_and_auto_close(
                linked_indicator_values, session, self.client
            )

        logger.info(f"{timeframe.label}: Сохранение результатов в файлы")

        save_market_data(df_candles, timeframe)
        save_signals(signals, timeframe)
        save_indicators(indicators, timeframe)
        save_linked_values(linked_indicator_values, timeframe)

        self.state_manager.set_updated(timeframe)
        
        await self.broadcaster.signals_updated(timeframe)

        logger.info(f"{timeframe.label}: Обновление завершено")

    async def update_price_volume(self, df):
        self.price_volume_monitor.calculate_and_save(df)
        await self.broadcaster.price_volume_updated()
