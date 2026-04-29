from enum import Enum
from pydantic import BaseModel, field_serializer

from .timeframe import Timeframe


class Direction(str, Enum):
    UP = "ВВЕРХ"
    DOWN = "ВНИЗ"


class Indicator(str, Enum):
    RSI = "RSI"
    MACD = "MACD"
    EMA_SMA = "EMA_SMA"


class Signal(BaseModel):
    symbol: str
    indicator: Indicator
    indicator_value: float
    direction: Direction
    vol_ratio: float
    correlation: float
    timeframe: Timeframe

    @field_serializer("timeframe")
    def serialize_timeframe(self, tf: Timeframe):
        return tf.label