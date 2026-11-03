from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Direction(str, Enum):
    UP = "ВВЕРХ"
    DOWN = "ВНИЗ"


class Indicator(str, Enum):
    RSI = "rsi"
    MACD = "macd"
    EMA_SMA = "emaSma"
    VOL_RATIO = "volRatio"


class OscillatorSignal(BaseModel):
    symbol: str
    indicator: Literal[Indicator.RSI]
    value: float
    direction: Direction
    vol_ratio: float
    correlation: float


class CrossoverSignal(BaseModel):
    symbol: str
    indicator: Literal[Indicator.MACD, Indicator.EMA_SMA]
    strength: float
    direction: Direction
    vol_ratio: float
    correlation: float


Signal = Annotated[OscillatorSignal | CrossoverSignal, Field(discriminator="indicator")]