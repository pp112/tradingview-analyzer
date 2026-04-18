from typing import Literal

from config import get_logger
from models.timeframe import Timeframe
from market import MarketDataClient
from processing import IndicatorEngine, ReportBuilder
from config.settings import load_settings
from utils import read_correlations
from storage.writer import (
    save_indicators,
    save_signals,
    save_correlations,
    save_report,
    save_market_data
)

logger = get_logger(__name__, "[UPDATER]")


class TimeframeUpdater:
    """
    Пайплайн обновления данных для конкретного таймфрейма.

    Выполняет:
    - загрузку исторических TOHLC данных
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
        self.report_builder = ReportBuilder()

    async def update(self, timeframe: Timeframe):
        """
        Выполняет полный цикл обновления данных для заданного таймфрейма.
        """
        logger.info(f"{timeframe.label}: Старт пайплайна")

        threshold, sort_order = self._get_correlation_settings()

        df = await self.market_client.get_all_historical_tohlc(timeframe)

        indicators, signals = self.indicator_engine.process(df, timeframe)

        if timeframe == Timeframe.H1:
            correlations = self.indicator_engine.calculate_correlations(df, sort_order)
            save_correlations(correlations)

            logger.info("Корреляции пересчитаны и сохранены")

        reports_all = self.report_builder.build(
            signals,
            indicators,
            timeframe,
            correlations=read_correlations(),
            sort_order=sort_order
        )
        reports_low_corr = self.report_builder.build(
            signals,
            indicators,
            timeframe,
            correlations=read_correlations(),
            sort_order=sort_order,
            corr_threshold=threshold
        )

        save_market_data(df, timeframe)
        save_indicators(indicators, timeframe)
        save_signals(signals, timeframe)
        save_report(reports_all, timeframe)
        save_report(reports_low_corr, timeframe, suffix=f"_corr_{threshold}")

        logger.info(f"{timeframe.label}: Обновление завершено")

    def _get_correlation_settings(self) -> tuple[float, Literal["asc", "desc"]]:
        settings = load_settings()

        threshold = self._corr_threshold_override
        sort_order = self._corr_sort_order_override
        
        if threshold is None:
            threshold = settings.correlation.threshold
        if sort_order is None:
            sort_order = settings.correlation.sort_order

        return threshold, sort_order