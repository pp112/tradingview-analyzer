from functools import lru_cache

from backend.exchanges.base import ExchangeClient
from backend.exchanges.noop import NoOpExchangeClient
from backend.exchanges.bybit.client import ByBitClient
from backend.exchanges.credentials import load_bybit_credentials


@lru_cache
def get_bybit_client() -> ExchangeClient:
    """
    Создаёт (и кеширует) единственный экземпляр ByBitClient за всё время жизни приложения.
    Если API-ключей нет - заглушка.
    """
    credentials = load_bybit_credentials()
    if credentials is None:
        return NoOpExchangeClient()

    return ByBitClient(
        api_key=credentials.api_key, 
        api_secret=credentials.api_secret
    )
