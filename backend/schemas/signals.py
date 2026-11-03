from typing import Annotated, Literal

from pydantic import Field

from backend.schemas.base import ApiModel
from backend.models.signal import Direction, Indicator


class OscillatorSignalResponse(ApiModel):
    symbol: str
    indicator: Literal[Indicator.RSI]
    value: float
    direction: Direction
    vol_ratio: float
    correlation: float


class CrossoverSignalResponse(ApiModel):
    symbol: str
    indicator: Literal[Indicator.MACD, Indicator.EMA_SMA]
    strength: float
    direction: Direction
    vol_ratio: float
    correlation: float


SignalResponse = Annotated[
    OscillatorSignalResponse | CrossoverSignalResponse, 
    Field(discriminator="indicator")
]