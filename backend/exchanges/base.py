from abc import ABC, abstractmethod

from backend.exchanges.models import Order, Position


class ExchangeClient(ABC):
    """
    Абстрактный интерфейс биржевого клиента.
    """
    @abstractmethod
    async def get_positions(self) -> list[Position]:
        """
        Возвращает список открытых позиций.
        При ошибке — пустой список.
        """
        ...

    @abstractmethod
    async def get_orders(self) -> list[Order]:
        """
        Возвращает список открытых ордеров.
        При ошибке — пустой список.
        """
        ...

    @abstractmethod
    async def get_balance(self) -> float | None:
        """
        Возвращает текущий баланс аккаунта.
        При ошибке — None.
        """
        ...

    @abstractmethod
    async def close_position(self, position: Position) -> bool:
        """
        Закрывает открытую позицию рыночным ордером.
        True — успешно закрыта, False — ошибка.
        """
        ...

    @abstractmethod
    async def cancel_order(self, order: Order) -> bool:
        """
        Отменяет открытый ордер.
        True — успешно отменён, False — ошибка.
        """
        ...