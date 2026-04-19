class SignalScorer:
    """
    Класс для расчета "силы" сигнала.
    """
    @staticmethod
    def strength(signal_name: str, values: dict) -> float:
        """
        Возвращает "силу" сигнала.
        Логика:
        - RSI: расстояние до границ (0 или 100)
        - MACD: расстояние между MACD и signal
        - EMA/SMA: расстояние между линиями
        """
        if signal_name in {"RSI_OVERBOUGHT", "RSI_OVERSOLD"}:
            rsi = values.get("rsi")
            if rsi is None:
                return 0.0
            return rsi if signal_name == "RSI_OVERBOUGHT" else 100 - rsi

        if signal_name in {"MACD_BULLISH", "MACD_BEARISH"}:
            macd = values.get("macd", {})
            curr = macd.get("curr")
            if not curr:
                return 0.0
            return abs(curr["MACD"] - curr["MACD_signal"])

        if signal_name in {"EMA_SMA_BULLISH", "EMA_SMA_BEARISH"}:
            ema = values.get("ema")
            sma = values.get("sma")
            if not ema or not sma:
                return 0.0
            return abs(ema[1] - sma[1])

        return 0.0