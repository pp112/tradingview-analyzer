from typing import Literal

from processing.reporting.scorer import SignalScorer
from models.sort_mode import SortMode


class SignalSorter:
    """
    Класс для сортировки торговых сигналов.
    """
    @staticmethod
    def by_priority(
        signals: list[dict[str, str]],
        indicators: dict[str, dict],
        correlations: dict[str, float],
        corr_sort_order: Literal["asc", "desc"],
        sort_mode: SortMode
    ) -> list[dict[str, str]]:
        """
        Сортирует список торговых сигналов по составному ключу.
        
        Приоритеты:
        1. Тип индикатора (RSI -> MACD -> EMA/SMA)
        2. Сила сигнала (чем больше, тем выше)
        3. Объем относительно среднего значения
        4. Корреляция
        """
        indicator_priority = {
            "RSI_OVERBOUGHT": 0,
            "RSI_OVERSOLD": 0,
            "MACD_BULLISH": 1,
            "MACD_BEARISH": 1,
            "EMA_SMA_BULLISH": 2,
            "EMA_SMA_BEARISH": 2,
        }

        def key(signal: dict[str, str]) -> tuple[int, float, float, float]:
            """
            Возвращает кортеж для сортировки для сигнала.
            """
            symbol = signal["symbol"]
            signal_name = str(signal.get("signal", ""))
            indicator_values = indicators.get(symbol, {})

            priority = indicator_priority.get(signal_name, 99)
            indicator_strength = SignalScorer.strength(signal_name, indicator_values)
            volume_ratio = indicator_values.get("volume", {}).get("ratio", 0)

            corr_value = correlations.get(symbol, 0.0)
            corr_score = corr_value if corr_sort_order == "asc" else -corr_value

            if sort_mode == SortMode.CORR_IND_VOL:
                return (priority, corr_score, -indicator_strength, -volume_ratio)
            elif sort_mode == SortMode.VOL_IND_CORR:
                return (priority, -volume_ratio, -indicator_strength, corr_score)
            elif sort_mode == SortMode.IND_VOL_CORR:
                return (priority, -indicator_strength, -volume_ratio, corr_score)

        return sorted(signals, key=key)