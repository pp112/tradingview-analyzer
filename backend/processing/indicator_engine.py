import pandas as pd

from backend.processing import calculate_indicators, generate_signals
from backend.models import Timeframe, Signal
from backend.config import get_logger

logger = get_logger(__name__, "[SIGNALS]")


def process_indicators(
    df: pd.DataFrame,
    correlations: dict[str, float],
    timeframe: Timeframe
) -> tuple[
    dict[str, dict],
    list[Signal],
]:
    """
    Возвращает расчитанные индикаторы и сгенерированные сигналы
    """
    logger.info(f"{timeframe.label}: Расчёт индикаторов")
    indicators = calculate_indicators(df, timeframe)

    logger.info(f"{timeframe.label}: Генерация сигналов")
    signals = generate_signals(indicators, correlations)

    return indicators, signals
