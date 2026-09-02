from enum import Enum
from pydantic import BaseModel


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
