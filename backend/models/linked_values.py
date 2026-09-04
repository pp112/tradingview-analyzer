from pydantic import BaseModel

from backend.models.signal import Indicator


class CurrentIndicatorValue(BaseModel):
    """
    Текущее значение индикатора для привязанного сигнала.
    """
    symbol: str
    indicator: Indicator
    value: float