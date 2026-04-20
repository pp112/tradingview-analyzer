from typing import Literal

from processing.reporting.pipeline import ReportPipeline
from models.timeframe import Timeframe
from models.sort_mode import SortMode
from storage.writer import save_report
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
                ├── full/
                │   └── <timeframe>/
                │       └── <sort_mode>.txt
                └── low_corr/
                    └── <timeframe>/
                        └── <sort_mode>.txt
        """
        sort_modes = [
            SortMode.CORR_IND_VOL,
            SortMode.VOL_IND_CORR,
            SortMode.IND_VOL_CORR
        ]

        correlations = read_correlations()

        def build_and_save(threshold: float, group: str):
            for mode in sort_modes:
                reports_all = ReportPipeline.build(
                    signals=signals,
                    indicators=indicators,
                    timeframe=timeframe,
                    correlations=correlations,
                    corr_threshold=threshold,
                    corr_sort_order=corr_sort_order,
                    sort_mode=mode
                )
            
                save_report(reports_all, timeframe, group=group, sort_mode=mode)

        build_and_save(1, "full")

        if corr_threshold < 1:
            build_and_save(corr_threshold, "low_corr")
