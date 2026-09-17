from backend.schemas.base import ApiModel
from backend.exchanges.models import Side


class OrderResponse(ApiModel):
    exchange_order_id: str
    symbol: str
    side: Side
    created_at: int