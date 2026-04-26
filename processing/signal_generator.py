from models import Signal, Timeframe, Direction, Indicator


class SignalGenerator:
    """
    Генерирует торговые сигналы на основе уже рассчитанных индикаторов.
    """
    def __init__(self, upper_rsi: float, lower_rsi: float):
        self.upper_rsi = upper_rsi
        self.lower_rsi = lower_rsi

    def generate(
        self,
        indicators: dict[str, dict],
        correlations: dict[str, float],
        timeframe: Timeframe
    ) -> list[Signal]:
        """
        Генерирует список сигналов по всем символам.
        """
        signals = []
        
        for symbol, data in indicators.items():
            for signal_data in (
                self._rsi(data),
                self._macd(data),
                self._ma(data),
            ):
                if signal_data is None:
                    continue

                indicator, indicator_value, direction = signal_data
                signals.append(
                    Signal(
                        symbol=symbol,
                        indicator=indicator,
                        indicator_value=indicator_value,
                        direction=direction,
                        correlation=correlations[symbol],
                        timeframe=timeframe
                    )
                )

        return signals

    def _rsi(self, data: dict[str, dict]) -> list[Signal] | None:
        value = data.get("rsi")

        if value is None:
            return None

        if value > self.upper_rsi:
            direction = Direction.DOWN
        elif value < self.lower_rsi:
            direction = Direction.UP
        else:
            return None
        
        return Indicator.RSI, value, direction

    def _macd(self, data: dict[str, dict]) -> list[Signal] | None:
        block = data.get("macd") or {}
        prev = block.get("prev")
        curr = block.get("curr")

        if prev is None or curr is None:
            return None

        spread = abs(curr["MACD"] - curr["MACD_signal"])
        base = abs(curr["MACD_signal"]) if curr["MACD_signal"] != 0 else 1e-9
        value = spread / base

        if (
            prev["MACD"] < prev["MACD_signal"]
            and curr["MACD"] > curr["MACD_signal"]
            and curr["MACD"] < 0
            and curr["MACD_signal"] < 0
        ):
            direction = Direction.UP
        elif (
            prev["MACD"] > prev["MACD_signal"]
            and curr["MACD"] < curr["MACD_signal"]
            and curr["MACD"] > 0
            and curr["MACD_signal"] > 0
        ):
            direction = Direction.UP
        else:
            return None
        
        return Indicator.MACD, value, direction

    def _ma(self, data: dict[str, dict]) -> list[Signal] | None:
        ema = data.get("ema")
        sma = data.get("sma")

        if ema is None or sma is None:
            return None

        ema_prev, ema_curr = ema
        sma_prev, sma_curr = sma
        value = abs(ema_curr - sma_curr)

        if ema_prev < sma_prev and ema_curr > sma_curr:
            direction = Direction.UP
        elif ema_prev > sma_prev and ema_curr < sma_curr:
            direction = Direction.DOWN
        else:
            return None
        
        return Indicator.EMA_SMA, value, direction
