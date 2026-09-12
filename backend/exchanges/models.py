from pydantic import BaseModel
from enum import Enum


class Side(Enum):
    LONG = "long"
    SHORT = "short"


class Order(BaseModel):
    id: str
    symbol: str
    side: Side
    created_at: int
    

class Position(BaseModel):
    symbol: str
    side: Side
    pnl: float
    pnlPct: float | None
    size: float
    created_at: int


class PositionOut(BaseModel):
    symbol: str
    side: Side
    pnl: float
    pnlPct: float | None
    created_at: int