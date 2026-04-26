from typing import Literal

from processing.reporting.scorer import SignalScorer
from models import SortMode, Signal, Indicator


class SignalSorter:
    """
    Класс для сортировки торговых сигналов.
    """
    @staticmethod
    def by_priority(
        signals: list[Signal],
        indicators: dict[str, dict],
        correlations: dict[str, float],
        corr_sort_order: Literal["asc", "desc"],
        sort_mode: SortMode
    ) -> list[Signal]:
        """
        Сортирует список торговых сигналов по составному ключу.
        
        Приоритеты:
        1. Тип индикатора (RSI -> MACD -> EMA/SMA)
        2. Сила сигнала (чем больше, тем выше)
        3. Объем относительно среднего значения
        4. Корреляция
        """
        indicator_priority = {
            Indicator.RSI: 0,
            Indicator.MACD: 1,
            Indicator.EMA_SMA: 2,
        }

        def key(s: Signal) -> tuple[int, float, float, float]:
            """
            Возвращает кортеж для сортировки для сигнала.
            """
            indicator_values = indicators.get(s.symbol, {})
            priority = indicator_priority.get(s.indicator, 99)
            strength = SignalScorer.strength(s, indicator_values)
            volume_ratio = indicator_values.get("volume", {}).get("ratio", 0)
            corr_value = correlations.get(s.symbol, 0.0)
            corr_score = corr_value if corr_sort_order == "asc" else -corr_value

            if sort_mode == SortMode.CORR_IND_VOL:
                return (priority, corr_score, -strength, -volume_ratio)
            elif sort_mode == SortMode.VOL_IND_CORR:
                return (priority, -volume_ratio, -strength, corr_score)
            elif sort_mode == SortMode.IND_VOL_CORR:
                return (priority, -strength, -volume_ratio, corr_score)

        return sorted(signals, key=key)