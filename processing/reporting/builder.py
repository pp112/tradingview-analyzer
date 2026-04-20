from typing import Literal
from collections import defaultdict

from processing.reporting.pipeline import ReportPipeline
from visualization.plotter import MarketPlotter
from models.timeframe import Timeframe
from models.sort_mode import SortMode
from storage.writer import save_report, ensure_dir
from utils import read_correlations


class ReportBuilder:
    """
    Формирует и сохраняет отчёты по торговым сигналам.

    Пайплайн:
    1. Загрузка корреляций
    2. Фильтрация сигналов по корреляции
    3. Сортировка сигналов по приоритету
    4. Формирование строк отчёта
    5. Сохранение отчётов 
    """
    def __init__(self):
        self.plotter = MarketPlotter()

    def generate_and_save_reports(
        self,
        signals: list[dict[str, str]],
        indicators: dict[str, dict],
        timeframe: Timeframe,
        corr_sort_order: Literal["asc", "desc"],
        corr_threshold: float = 1
    ):
        """
        Генерирует и сохраняет отчёты по торговым сигналам.

        - для каждого режима сортировки формируются 2 типа отчётов:
            1. Полный список сигналов (без фильтра по корреляции)
            2. Отфильтрованный список (с учётом corr_threshold)

        - отчёты сохраняются в структуру:
            data/reports/
                ├── full-low_corr/
                    └── timeframe/
                        └── sort_mode.txt
                        └── indicator_type/
                            └── 1.jpg, 2.jpg,
        """
        sort_modes = [
            SortMode.CORR_IND_VOL,
            SortMode.VOL_IND_CORR,
            SortMode.IND_VOL_CORR
        ]

        correlations = read_correlations()
        import time
        def build_and_save(threshold: float, group: str):
            for mode in sort_modes:
                reports, sorted_signals = ReportPipeline.build(
                    signals=signals,
                    indicators=indicators,
                    timeframe=timeframe,
                    correlations=correlations,
                    corr_threshold=threshold,
                    corr_sort_order=corr_sort_order,
                    sort_mode=mode
                )
            
                save_report(reports, timeframe, group=group, sort_mode=mode)

                if sorted_signals:
                    start = time.time()
                    self._save_charts(
                        signals=sorted_signals,
                        timeframe=timeframe,
                        group=group,
                        sort_mode=mode,
                        max_charts=5
                    )
                    print(f"Затрачено на графики {timeframe}: {time.time() - start}")

        build_and_save(1, "full")

        if corr_threshold < 1:
            build_and_save(corr_threshold, "low_corr")

    def _save_charts(
        self,
        signals: list[dict[str, str]],
        timeframe: Timeframe,
        group: str,
        sort_mode: SortMode,
        max_charts: int
    ):
        """
        Сохраняет графики для сигналов, группируя их по типу индикатора.
        """
        signals_by_indicator = defaultdict(list)

        for signal in signals:
            signal_type = signal["signal"]

            if "RSI" in signal_type:
                indicator_type = "RSI"
            elif "MACD" in signal_type:
                indicator_type = "MACD"
            elif "EMA_SMA" in signal_type:
                indicator_type = "EMA_SMA"

            signals_by_indicator[indicator_type].append(signal)

        for indicator_type, indicator_signals in signals_by_indicator.items():
            top_signals = indicator_signals[:max_charts]
            if not top_signals:
                continue

            charts_folder = (
                f"data/reports/{group}/{timeframe.label}/"
                f"{sort_mode.charts_dirname}/{indicator_type}"
            )
            ensure_dir(charts_folder)

            for i, signal in enumerate(top_signals, start=1):
                symbol = signal["symbol"]

                self.plotter.plot_candles(
                    symbol=symbol,
                    save_folder=charts_folder,
                    filename=str(i),
                    timeframe=timeframe
                )
            