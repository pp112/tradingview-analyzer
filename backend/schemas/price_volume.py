from backend.schemas.base import ApiModel


class PriceVolumeResponse(ApiModel):
    symbol: str
    price_delta_pct: float
    volume_delta_pct: float
