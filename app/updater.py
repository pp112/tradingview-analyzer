from typing import Literal

from models import Timeframe
from market import MarketDataClient
from processing import IndicatorEngine, ReportBuilder, CorrelationCalculator, PriceVolumeMonitor
from config.settings import load_settings
from utils import read_correlations
from storage.writer import (
    save_indicators,
    save_signals,
    save_correlations,
    save_market_data
)
from api.api import broadcast
from config import get_logger

logger = get_logger(__name__, "[UPDATER]")


class TimeframeUpdater:
    """
    Пайплайн обновления данных для конкретного таймфрейма.

    Выполняет:
    - загрузку исторических данных свечей
    - расчет индикаторов и сигналов
    - расчёт корреляций (для H1)
    - сохранение результатов
    """
    def __init__(
        self,
        corr_threshold: float | None = None,
        corr_sort_order: Literal["asc", "desc"] | None = None
    ):
        self._corr_threshold_override = corr_threshold
        self._corr_sort_order_override = corr_sort_order

        self.market_client = MarketDataClient()
        self.indicator_engine = IndicatorEngine()
        self.correlation_calculator = CorrelationCalculator()
        self.price_volume_monitor = PriceVolumeMonitor()
        self.report_builder = ReportBuilder()

    async def update(self, timeframe: Timeframe):
        """
        Выполняет полный цикл обновления данных для заданного таймфрейма.
        """
        logger.info(f"{timeframe.label}: Старт пайплайна")

        corr_threshold, corr_sort_order = self._resolve_correlation_settings()

        df_candles = await self.market_client.fetch_all_historical_candles(timeframe)

        if timeframe == Timeframe.M30:
            self.price_volume_monitor.calculate_and_save(df_candles)
            await broadcast({"type": "price_volume"})

        if timeframe == Timeframe.H1:
            logger.info(f"{timeframe.label}: Расчет корреляций")
            correlations = self.correlation_calculator.calculate(df_candles, corr_sort_order)
            save_correlations(correlations)
        else:
            correlations = read_correlations()

        indicators, signals = self.indicator_engine.process(
            df_candles, correlations, timeframe
        )
        
        logger.info(f"{timeframe.label}: Сохранение результатов в файлы")
        
        save_signals(signals, timeframe)

        await broadcast({"type": "signals", "timeframe": timeframe.label})

        save_market_data(df_candles, timeframe)
        save_indicators(indicators, timeframe)
        
        self.report_builder.generate_and_save_reports(
            signals=signals,
            indicators=indicators,
            timeframe=timeframe,
            corr_sort_order=corr_sort_order,
            corr_threshold=corr_threshold
        )

        logger.info(f"{timeframe.label}: Обновление завершено")

    def _resolve_correlation_settings(self) -> tuple[float, Literal["asc", "desc"]]:
        settings = load_settings()

        return (
            self._corr_threshold_override or settings.correlation.corr_threshold,
            self._corr_sort_order_override or settings.correlation.corr_sort_order
        )