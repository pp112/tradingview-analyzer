class SignalFilter:
    """
    Класс для фильтрации торговых сигналов.
    """
    @staticmethod
    def by_correlation(
        signals: list[dict[str, str]],
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
            if correlations.get(str(s["symbol"])) is not None
            and correlations[str(s["symbol"])] <= threshold
        ]
    
    @staticmethod
    def strong(
        signals: list[dict[str, str]],
        indicators: dict[str, dict],
        rsi_upper: float = 80,
        rsi_lower: float = 20,
        macd_strength_threshold: float = 0.5,
        volume_threshold: float | None = 2
    ) -> list[dict]:
        """
        Возвращает список сигналов с комбинированными сигналами
        """
        result = []
        for signal in signals:
            symbol = signal["symbol"]
            data = indicators.get(symbol)

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

            result.append(signal)
        return result