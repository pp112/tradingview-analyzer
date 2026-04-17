import logging
import os
from typing import Literal

from models.timeframe import Timeframe
from market import MarketDataClient
from processing import IndicatorEngine, ReportBuilder
from utils import read_correlations
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
    def __init__(
        self,
        corr_threshold: float | None = None,
        corr_sort_order: Literal["asc", "desc"] | None = None
    ):
        env_threshold = os.getenv("CORR_THRESHOLD")
        env_sort_order = os.getenv("CORR_SORT_ORDER", "desc").lower()

        resolved_threshold = float(env_threshold) if env_threshold is not None else 0.5
        resolved_sort_order = env_sort_order if env_sort_order in ("asc", "desc") else "desc"

        if corr_threshold is not None:
            resolved_threshold = corr_threshold

        if corr_sort_order is not None:
            resolved_sort_order = corr_sort_order

        self.corr_threshold = resolved_threshold
        self.corr_sort_order = resolved_sort_order

        self.market_client = MarketDataClient()
        self.indicator_engine = IndicatorEngine(corr_sort_order=resolved_sort_order)
        self.report_builder = ReportBuilder()


    async def update(self, timeframe: Timeframe):
        """
        Выполняет полный цикл обновления данных для заданного таймфрейма.
        """
        logger.info(f"Начинаем обновление таймфрейма: {timeframe.label}")

        df = await self.market_client.get_all_historical_tohlc(timeframe)

        indicators, signals = self.indicator_engine.process(df, timeframe)
        
        if timeframe == Timeframe.H1:
            correlations = self.indicator_engine.calculate_correlations(df)
            save_correlations(correlations)

            logger.info("Обновлены значения корреляций")

        reports_all = self.report_builder.build(
            signals,
            timeframe,
            correlations=read_correlations(),
            sort_order=self.corr_sort_order
        )
        reports_low_corr = self.report_builder.build(
            signals,
            timeframe,
            correlations=read_correlations(),
            sort_order=self.corr_sort_order,
            corr_threshold=self.corr_threshold
        )

        save_indicators(indicators, timeframe)
        save_signals(signals, timeframe)
        save_report(reports_all, timeframe)
        save_report(reports_low_corr, timeframe, suffix=f"_corr_{self.corr_threshold}")

        logger.info(f"Завершено обновление: {timeframe.label}")