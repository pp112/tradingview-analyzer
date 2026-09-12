import os
from dataclasses import dataclass

from backend.config import get_logger

logger = get_logger(__name__, "[CREDENTIALS]")


@dataclass(frozen=True)
class ExchangeCredentials:
    api_key: str
    api_secret: str


def load_bybit_credentials() -> ExchangeCredentials | None:
    api_key = os.getenv("BYBIT_API_KEY")
    api_secret = os.getenv("BYBIT_API_SECRET")

    if not api_key or not api_secret:
        logger.warning("Данные API BYBIT не загружены.")
        return None

    return ExchangeCredentials(api_key=api_key, api_secret=api_secret)