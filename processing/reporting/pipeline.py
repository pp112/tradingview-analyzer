from typing import Literal

from models import SortMode, Signal
from processing.reporting.filter import SignalFilter
from processing.reporting.sorter import SignalSorter
from processing.reporting.formatter import ReportFormatter


class ReportPipeline:
    """
    Pipeline формирования отчёта по торговым сигналам.

    Шаги:
    1. Фильтрация сигналов по корреляции
    2. Сортировка сигналов
    3. Формирование строк отчёта
    """
    @staticmethod
    def build(
        signals: list[Signal],
        indicators: dict[str, dict],
        correlations: dict[str, float],
        corr_threshold: float,
        corr_sort_order: Literal["asc", "desc"],
        sort_mode: SortMode
    ) -> tuple[list[str], list[Signal]]:
        """
        Формирует список строк отчёта.
        """
        filtered_signals = SignalFilter.by_correlation(
            signals=signals,
            correlations=correlations,
            threshold=corr_threshold
        )

        sorted_signals = SignalSorter.by_priority(
            signals=filtered_signals,
            indicators=indicators,
            correlations=correlations,
            corr_sort_order=corr_sort_order,
            sort_mode=sort_mode
        )

        reports = [
            ReportFormatter.format_line(
                signal=s,
                corr_value=correlations.get(s.symbol),
                indicator_values=indicators.get(s.symbol, {}),
                column_order=sort_mode,
                index=i
            )
            for i, s in enumerate(sorted_signals, start=1)
        ]

        return reports, sorted_signals