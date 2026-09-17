from backend.schemas.base import ApiModel


class BalanceResponse(ApiModel):
    balance: float | None