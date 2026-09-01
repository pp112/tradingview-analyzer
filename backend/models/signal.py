from enum import Enum
from pydantic import BaseModel, field_serializer

from .timeframe import Timeframe


class Direction(str, Enum):
    UP = "ВВЕРХ"
    DOWN = "ВНИЗ"


class Indicator(str, Enum):
    RSI = "rsi"
    MACD = "macd"
    EMA_SMA = "ema_sma"
    VOL_RATIO = "vol_ratio"


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

    @field_serializer("symbol")
    def serialize_symbol(self, symbol: str):
        return symbol.replace(".P", "").replace("USDT", "/USDT")