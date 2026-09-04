from backend.models import Signal, Direction, Indicator


def generate_signals(
    indicators: dict[str, dict],
    correlations: dict[str, float]
) -> list[Signal]:
    """
    Генерирует список сигналов по всем символам.
    """
    signals = []
    
    for symbol, data in indicators.items():
        for signal_data in (
            _rsi(data),
            _macd(data),
            _ma(data),
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
                    vol_ratio=indicators[symbol]["volume"]["ratio"],
                    correlation=correlations[symbol]
                )
            )

    return signals

def _rsi(data: dict[str, dict]) -> tuple[Indicator, float, Direction] | None:
    value = data.get("rsi")

    if value is None:
        return None

    if value > 70:
        direction = Direction.DOWN
    elif value < 30:
        direction = Direction.UP
    else:
        return None
    
    return Indicator.RSI, value, direction

def _macd(data: dict[str, dict]) -> tuple[Indicator, float, Direction] | None:
    block = data.get("macd") or {}
    prev = block.get("prev")
    curr = block.get("curr")

    if prev is None or curr is None:
        return None

    value = abs(curr["MACD"])

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
        direction = Direction.DOWN
    else:
        return None
    
    return Indicator.MACD, value, direction

def _ma(data: dict[str, dict]) -> tuple[Indicator, float, Direction] | None:
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
