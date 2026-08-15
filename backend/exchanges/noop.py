from backend.exchanges.base import ExchangeClient
from backend.exchanges.models import Order, Position


class NoOpExchangeClient(ExchangeClient):
    """
    Заглушка биржевого клиента.
    Используется когда API-ключи не заданы.
    """

    async def get_positions(self) -> list[Position]:
        return []

    async def get_orders(self) -> list[Order]:
        return []

    async def get_balance(self) -> float | None:
        return None

    async def close_position(self, position: Position) -> bool:
        return False

    async def cancel_order(self, order: Order) -> bool:
        return False