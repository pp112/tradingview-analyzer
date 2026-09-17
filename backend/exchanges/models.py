from enum import Enum

from pydantic import BaseModel


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"


class Order(BaseModel):
    exchange_order_id: str
    symbol: str
    side: Side
    created_at: int
    

class Position(BaseModel):
    symbol: str
    side: Side
    pnl: float
    pnl_pct: float | None
    size: float
    created_at: int
