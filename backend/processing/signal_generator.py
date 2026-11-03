from dataclasses import dataclass

from backend.models import Signal, Direction, Indicator
from backend.models.signal import CrossoverSignal, OscillatorSignal


# Максимальный "возраст" пересечения в барах, чтобы считать его актуальным
MACD_MAX_SIGNAL_AGE = 5
EMA_SMA_MAX_SIGNAL_AGE = 7


@dataclass
class RawOscillator:
    indicator: Indicator
    value: float
    direction: Direction

    def to_signal(self, symbol: str, vol_ratio: float, correlation: float) -> OscillatorSignal:
        return OscillatorSignal(
            symbol=symbol, indicator=self.indicator, value=self.value,
            direction=self.direction, vol_ratio=vol_ratio, correlation=correlation
        )


@dataclass
class RawCrossover:
    indicator: Indicator
    strength: float
    direction: Direction

    def to_signal(self, symbol: str, vol_ratio: float, correlation: float) -> CrossoverSignal:
        return CrossoverSignal(
            symbol=symbol, indicator=self.indicator, strength=self.strength,
            direction=self.direction, vol_ratio=vol_ratio, correlation=correlation
        )


def generate_signals(
    indicators: dict[str, dict],
    correlations: dict[str, float]
) -> list[Signal]:
    """
    Генерирует список сигналов по всем символам.
    """
    signals = []
    
    for symbol, data in indicators.items():
        if symbol not in correlations:
            continue

        vol_ratio = data["volume"]["ratio"]
        correlation = correlations[symbol]

        for raw in (_rsi(data), _macd(data), _ema_sma(data)):
            if raw is not None:
                signals.append(raw.to_signal(symbol, vol_ratio, correlation))

    return signals


def _rsi(data: dict) -> RawOscillator | None:
    value = data.get("rsi")
    if value is None:
        return None

    if value > 70:
        return RawOscillator(indicator=Indicator.RSI, value=value, direction=Direction.DOWN)
    elif value < 30:
        return RawOscillator(indicator=Indicator.RSI, value=value, direction=Direction.UP)
    else:
        return None


def _macd(data: dict) -> RawCrossover | None:
    """
    Формирование данных сигнала MACD: актуальность, направление и сила.
    None — если пересечения нет, оно устарело или силу не из чего посчитать.
    """
    block = data.get("macd") or {}
    crossover = block.get("latest_crossover")
    strength = block.get("strength")
    if crossover is None or strength is None or not block.get("valid_zero_line"):
        return None

    age = block["bar_count"] - 1 - crossover.index
    if age > MACD_MAX_SIGNAL_AGE:
        return None
    
    return RawCrossover(Indicator.MACD, strength, crossover.direction)


def _ema_sma(data: dict) -> RawCrossover | None:
    """
    Формирование данных сигнала EMA/SMA: актуальность, направление и сила.
    None — если пересечения нет, оно устарело или силу не из чего посчитать.
    """
    block = data.get("ema_sma") or {}
    crossover = block.get("latest_crossover")
    strength = block.get("strength")
    if crossover is None or strength is None:
        return None

    age = block["bar_count"] - 1 - crossover.index
    if age > EMA_SMA_MAX_SIGNAL_AGE:
        return None
    
    return RawCrossover(Indicator.EMA_SMA, strength, crossover.direction)
