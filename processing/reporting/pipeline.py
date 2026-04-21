from typing import Literal

from models.sort_mode import SortMode
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
    MAPPING = {
        "RSI_OVERBOUGHT": ("RSI", "ВНИЗ"),
        "RSI_OVERSOLD": ("RSI", "ВВЕРХ"),
        "MACD_BULLISH": ("MACD", "ВВЕРХ"),
        "MACD_BEARISH": ("MACD", "ВНИЗ"),
        "EMA_SMA_BULLISH": ("EMA_SMA", "ВВЕРХ"),
        "EMA_SMA_BEARISH": ("EMA_SMA", "ВНИЗ"),
    }

    @staticmethod
    def build(
        signals: list[dict[str, str]],
        indicators: dict[str, dict],
        timeframe,
        correlations: dict[str, float],
        corr_threshold: float,
        corr_sort_order: Literal["asc", "desc"],
        sort_mode: SortMode
    ) -> tuple[
        list[str], 
        list[dict[str, str]]
    ]:
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

        reports = []

        for i, signal in enumerate(sorted_signals, start=1):
            signal_name = signal["signal"]
            symbol = str(signal["symbol"])

            indicator_name, direction = ReportPipeline.MAPPING.get(signal_name, ("-", "-"))

            corr_value = correlations.get(symbol)
            indicator_values = indicators.get(symbol, {})
            vol_ratio = indicator_values.get("volume", {}).get("ratio", 0)

            reports.append(
                ReportFormatter.format_line(
                    symbol=symbol,
                    direction=direction,
                    indicator_name=indicator_name,
                    timeframe=timeframe,
                    corr_value=corr_value,
                    indicator_values=indicator_values,
                    vol_ratio=vol_ratio,
                    column_order=sort_mode,
                    index=i
                )
            )

        return reports, sorted_signals