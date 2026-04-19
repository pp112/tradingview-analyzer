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