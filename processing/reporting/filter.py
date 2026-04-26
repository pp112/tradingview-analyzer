from models import Signal

class SignalFilter:
    """
    Класс для фильтрации торговых сигналов.
    """
    @staticmethod
    def by_correlation(
        signals: list[Signal],
        correlations: dict[str, float],
        threshold: float
    ) -> list[dict]:
        """
        Фильтрует список торговых сигналов по значению корреляции.

        Оставляет только те сигналы, у которых значение корреляции
        существует и не превышает заданный порог.
        """
        return [
            s for s in signals
            if correlations[s.symbol] <= threshold
        ]
    
    @staticmethod
    def strong(
        signals: list[Signal],
        indicators: dict[str, dict],
        rsi_upper: float = 80,
        rsi_lower: float = 20,
        macd_strength_threshold: float = 0.5,
        volume_threshold: float | None = 2
    ) -> list[Signal]:
        """
        Возвращает список сигналов с комбинированными сигналами
        """
        result = []
        for s in signals:
            data = indicators.get(s.symbol)

            rsi = data.get("rsi")
            if not (rsi > rsi_upper or rsi < rsi_lower):
                continue
            
            macd = data.get("macd").get("curr")
            spread = abs(macd["MACD"] - macd["MACD_signal"])
            base = abs(macd["MACD_signal"]) or 1e-9
            strength = spread / base
            if strength < macd_strength_threshold:
                continue

            if volume_threshold is not None:
                volume = data.get("volume").get("ratio")
                if volume <= volume_threshold:
                    continue

            result.append(s)
        return result