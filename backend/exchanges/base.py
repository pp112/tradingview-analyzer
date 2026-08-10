from abc import ABC, abstractmethod

class ExchangeClient(ABC):
    """
    Абстрактный интерфейс биржевого клиента.
    """
    @abstractmethod
    async def get_positions(self):
        ...

    @abstractmethod
    async def get_balance(self):
        ...

    @abstractmethod
    async def close_position(self):
        ...