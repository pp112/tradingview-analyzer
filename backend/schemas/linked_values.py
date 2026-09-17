from backend.schemas.base import ApiModel
from backend.models.signal import Indicator


class CurrentIndicatorValueResponse(ApiModel):
    """
    Текущее значение индикатора для привязанного сигнала.
    """
    symbol: str
    indicator: Indicator
    value: float