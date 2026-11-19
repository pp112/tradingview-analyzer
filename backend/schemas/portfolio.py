from backend.schemas.base import ApiModel
from backend.exchanges.models import Side


class OrderResponse(ApiModel):
    exchange_order_id: str
    symbol: str
    side: Side
    created_at: int


class PositionResponse(ApiModel):
    symbol: str
    side: Side
    pnl: float
    pnl_pct: float | None
    created_at: int


class PortfolioResponse(ApiModel):
    positions: list[PositionResponse]
    orders: list[OrderResponse]
    balance: float | None
    updated_at: int | None
    