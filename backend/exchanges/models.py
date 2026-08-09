from pydantic import BaseModel
from enum import Enum

class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"

class Position(BaseModel):
    symbol: str
    side: PositionSide
