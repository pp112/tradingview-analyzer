from backend.schemas.base import ApiModel
from backend.models.signal import Direction, Indicator


class SignalResponse(ApiModel):
    symbol: str
    indicator: Indicator
    indicator_value: float
    direction: Direction
    vol_ratio: float
    correlation: float