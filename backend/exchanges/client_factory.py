from backend.exchanges.base import ExchangeClient
from backend.exchanges.bybit.client import ByBitClient
from backend.exchanges.credentials import load_bybit_credentials
from backend.exchanges.noop import NoOpExchangeClient


def create_bybit_client() -> ExchangeClient:
    """
    Создаёт клиента биржи. Если API-ключей нет - заглушка.
    Вызывается один раз в App.
    """
    credentials = load_bybit_credentials()
    if credentials is None:
        return NoOpExchangeClient()

    return ByBitClient(
        api_key=credentials.api_key, 
        api_secret=credentials.api_secret
    )