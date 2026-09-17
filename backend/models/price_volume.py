from pydantic import BaseModel


class PriceVolume(BaseModel):
    """
    Изменения цен и объемов символа
    """
    symbol: str
    price_delta_pct: float
    volume_delta_pct: float
