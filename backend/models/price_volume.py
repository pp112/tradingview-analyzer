from pydantic import BaseModel, field_serializer


class PriceVolume(BaseModel):
    symbol: str
    price_delta_pct: float
    volume_delta_pct: float

    @field_serializer("symbol")
    def serialize_symbol(self, symbol: str):
        return symbol.replace(".P", "").replace("USDT", "/USDT")