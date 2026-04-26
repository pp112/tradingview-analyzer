from models import Signal, Indicator, Direction

class SignalScorer:
    """
    Класс для расчета "силы" сигнала.
    """
    @staticmethod
    def strength(signal: Signal, values: dict) -> float:
        """
        Возвращает "силу" сигнала.
        Логика:
        - RSI: расстояние до границ (0 или 100)
        - MACD: расстояние между MACD и signal
        - EMA/SMA: расстояние между линиями
        """
        if signal.indicator == Indicator.RSI:
            rsi = values.get("rsi")
            if rsi is None:
                return 0.0
            return rsi if signal.direction == Direction.DOWN else 100 - rsi

        if signal.indicator == Indicator.MACD:
            curr = values.get("macd", {}).get("curr")
            if not curr:
                return 0.0
            spread = abs(curr["MACD"] - curr["MACD_signal"])
            base = abs(curr["MACD_signal"]) if curr["MACD_signal"] != 0 else 1e-9
            return spread / base

        if signal.indicator == Indicator.EMA_SMA:
            ema = values.get("ema")
            sma = values.get("sma")
            if not ema or not sma:
                return 0.0
            return abs(ema[1] - sma[1])

        return 0.0