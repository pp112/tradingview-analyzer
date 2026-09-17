from backend.schemas.base import ApiModel
from backend.exchanges.models import Side


class PositionResponse(ApiModel):
    symbol: str
    side: Side
    pnl: float
    pnl_pct: float | None
    created_at: int