from backend.exchanges.base import ExchangeClient
from pybit.unified_trading import HTTP


class ByBitClient(ExchangeClient):
    """
    Клиент для работы в ByBit API.
    """

    def __init__(self, api_key: str, api_secret: str):
        self.session = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret
        )

    async def get_positions(self):
        res = self.session.get_wallet_balance(
            accountType="UNIFIED"
        )
        return res

    async def get_balance(self):
        pass

    async def close_position(self):
        pass


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import asyncio
    load_dotenv()

    client = ByBitClient(api_key=os.getenv("API_KEY_BYBIT"),
                         api_secret=os.getenv("API_SECRET_BYBIT"))

    print(asyncio.run(client.get_positions()))
