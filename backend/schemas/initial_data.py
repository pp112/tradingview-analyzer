from backend.schemas.base import ApiModel
from backend.schemas.signals import SignalResponse
from backend.schemas.price_volume import PriceVolumeResponse


class InitialDataResponse(ApiModel):
    signals: dict[str, list[SignalResponse]]
    price_changes: list[PriceVolumeResponse] | None