from models.timeframe import Timeframe


class SignalGenerator:
    """
    Генерирует торговые сигналы на основе уже рассчитанных индикаторов.
    """
    def __init__(self, upper_rsi, lower_rsi):
        self.upper_rsi = upper_rsi
        self.lower_rsi = lower_rsi

    def generate(
        self,
        indicators: dict[str, dict],
        timeframe: Timeframe
    ) -> list[dict]:

        signals = []

        for symbol, data in indicators.items():
            signals.extend(self._rsi(symbol, data, timeframe))
            signals.extend(self._macd(symbol, data, timeframe))
            signals.extend(self._ma(symbol, data, timeframe))

        return signals

    def _rsi(self, symbol, data, timeframe):
        rsi_val = data.get("rsi")
        signals = []

        if rsi_val is None:
            return signals

        if rsi_val > self.upper_rsi:
            signals.append({
                "symbol": symbol,
                "signal": "RSI_OVERBOUGHT",
                "timeframe": timeframe.value
            })

        elif rsi_val < self.lower_rsi:
            signals.append({
                "symbol": symbol,
                "signal": "RSI_OVERSOLD",
                "timeframe": timeframe.value
            })

        return signals

    def _macd(self, symbol, data, timeframe):
        signals = []

        macd_block = data.get("macd") or {}
        macd_prev = macd_block.get("prev")
        macd_curr = macd_block.get("curr")

        if macd_prev is None or macd_curr is None:
            return signals

        if (
            macd_prev["MACD"] < macd_prev["MACD_signal"]
            and macd_curr["MACD"] > macd_curr["MACD_signal"]
        ):
            signals.append({
                "symbol": symbol,
                "signal": "MACD_BULLISH",
                "timeframe": timeframe.value
            })

        elif (
            macd_prev["MACD"] > macd_prev["MACD_signal"]
            and macd_curr["MACD"] < macd_curr["MACD_signal"]
        ):
            signals.append({
                "symbol": symbol,
                "signal": "MACD_BEARISH",
                "timeframe": timeframe.value
            })

        return signals

    def _ma(self, symbol, data, timeframe):
        signals = []

        ema = data.get("ema")
        sma = data.get("sma")

        if ema is None or sma is None:
            return signals

        ema_prev, ema_curr = ema
        sma_prev, sma_curr = sma

        if ema_prev < sma_prev and ema_curr > sma_curr:
            signals.append({
                "symbol": symbol,
                "signal": "EMA_SMA_BULLISH",
                "timeframe": timeframe.value
            })

        elif ema_prev > sma_prev and ema_curr < sma_curr:
            signals.append({
                "symbol": symbol,
                "signal": "EMA_SMA_BEARISH",
                "timeframe": timeframe.value
            })

        return signals