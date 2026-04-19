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

        corr_threshold, corr_sort_order = self._get_correlation_settings()

        df = await self.market_client.get_all_historical_tohlc(timeframe)

        indicators, signals = self.indicator_engine.process(df, timeframe)

        if timeframe == Timeframe.H1:
            correlations = self.indicator_engine.calculate_correlations(df, corr_sort_order)
            save_correlations(correlations)

            logger.info(f"{timeframe.label}: Корреляции расчитаны и сохранены")

        logger.info(f"{timeframe.label}: Сохранение результатов в файлы")

        save_market_data(df, timeframe)
        save_indicators(indicators, timeframe)
        save_signals(signals, timeframe)
        
        self._generate_and_save_reports(
            signals,
            indicators,
            timeframe,
            corr_threshold,
            corr_sort_order
        )

        logger.info(f"{timeframe.label}: Обновление завершено")

    def _generate_and_save_reports(
        self,
        signals: list[dict[str, str]],
        indicators: dict[str, dict],
        timeframe: Timeframe,
        corr_threshold: float,
        corr_sort_order: Literal["asc", "desc"]
    ):
        """
        Генерирует и сохраняет отчёты по торговым сигналам.

        - для каждого режима сортировки формируются 2 типа отчётов:
            1. Полный список сигналов (без фильтра по корреляции)
            2. Отфильтрованный список (с учётом corr_threshold)

        - отчёты сохраняются в структуру:
            data/reports/
                ├── full/
                │   └── <timeframe>/
                │       └── <sort_mode>.txt
                └── low_corr/
                    └── <timeframe>/
                        └── <sort_mode>.txt
        """
        sort_modes = [
            "corr_indic_vol",
            "vol_indic_corr",
            "indic_vol_corr"
        ]

        correlations = read_correlations()

        for mode in sort_modes:
            reports_all = self.report_builder.build(
                signals,
                indicators,
                timeframe,
                correlations=correlations,
                corr_sort_order=corr_sort_order,
                sort_mode=mode
            )

            reports_filtered = self.report_builder.build(
                signals,
                indicators,
                timeframe,
                correlations=correlations,
                corr_sort_order=corr_sort_order,
                corr_threshold=corr_threshold,
                sort_mode=mode
            )

            save_report(reports_all, timeframe, group="full", sort_mode=mode)
            save_report(reports_filtered, timeframe, group="low_corr", sort_mode=mode)

    def _get_correlation_settings(self) -> tuple[float, Literal["asc", "desc"]]:
        settings = load_settings()

        corr_threshold = self._corr_threshold_override
        corr_sort_order = self._corr_sort_order_override
        
        if corr_threshold is None:
            corr_threshold = settings.correlation.corr_threshold
        if corr_sort_order is None:
            corr_sort_order = settings.correlation.corr_sort_order

        return corr_threshold, corr_sort_order