from pydantic import BaseModel


class PriceVolume(BaseModel):
    symbol: str
    price_delta_pct: float
    volume_delta_pct: float
