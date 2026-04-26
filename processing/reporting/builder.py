from typing import Literal
from collections import defaultdict
from multiprocessing import Pool, cpu_count

from processing.reporting.filter import SignalFilter
from processing.reporting.pipeline import ReportPipeline
from visualization.plotter import MarketPlotter
from models import Timeframe, SortMode, Signal
from storage.writer import save_report_txt, ensure_dir
from utils import read_correlations
from config import get_logger

logger = get_logger(__name__, "[REPORTS]")


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
        signals: list[Signal],
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

        def build_and_save(input_signals: list[dict[str, str]], corr_threshold: float, group: str):
            """
            Для каждого варианта сортировки:
            1. Формируется и сохраняется отчет (txt)
            2. Создаются графики
            """
            for mode in sort_modes:
                reports, sorted_signals = ReportPipeline.build(
                    signals=input_signals,
                    indicators=indicators,
                    correlations=correlations,
                    corr_threshold=corr_threshold,
                    corr_sort_order=corr_sort_order,
                    sort_mode=mode
                )

                save_report_txt(reports, timeframe, group=group, sort_mode=mode)

                if sorted_signals:
                    self._save_charts(
                        signals=sorted_signals,
                        timeframe=timeframe,
                        group=group,
                        sort_mode=mode,
                        max_charts=5
                    )

            logger.info(f"{timeframe.label}: Отчеты сформированы - {group}")
        
        groups = []

        strong_signals = SignalFilter.strong(signals, indicators)
        if not strong_signals:
            strong_signals = SignalFilter.strong(signals, indicators, volume_threshold=None)

        if strong_signals:
            groups.append(("strong_all", strong_signals))
            if corr_threshold < 1:
                groups.append(("strong_low_corr", strong_signals))

        if corr_threshold < 1:
            groups.append(("low_corr", signals))
        groups.append(("all", signals))

        for group_name, sigs in groups:
            threshold = corr_threshold if "low_corr" in group_name else 1
            build_and_save(sigs, threshold, group_name)

    def _save_charts(
        self,
        signals: list[Signal],
        timeframe: Timeframe,
        group: str,
        sort_mode: SortMode,
        max_charts: int
    ):
        """
        Сохраняет графики для сигналов, группируя их по типу индикатора.
        """
        signals_by_indicator = defaultdict(list)

        for s in signals:
            if "RSI" in s.indicator.value:
                indicator_type = "RSI"
            elif "MACD" in s.indicator.value:
                indicator_type = "MACD"
            elif "EMA_SMA" in s.indicator.value:
                indicator_type = "EMA_SMA"
            signals_by_indicator[indicator_type].append(s)

        tasks = []

        for indicator_type, indicator_signals in signals_by_indicator.items():
            top_signals = indicator_signals[:max_charts]
            if not top_signals:
                continue

            charts_folder = (
                f"data/reports/{timeframe.label}/{group}/"
                f"{sort_mode.charts_dirname}/{indicator_type}"
            )
            ensure_dir(charts_folder)

            for i, signal in enumerate(top_signals, start=1):
                tasks.append((s.symbol, charts_folder, str(i), timeframe))
            
        if tasks:
            with Pool(processes=cpu_count() // 2 + 1) as pool:
                pool.map(_plot_task, tasks)


def _plot_task(args):
    """
    Отдельная задача multiprocessing для создания графика
    """
    symbol, save_folder, filename, timeframe = args

    plotter = MarketPlotter()

    return plotter.plot_candles(
        symbol=symbol,
        save_folder=save_folder,
        filename=filename,
        timeframe=timeframe
    )