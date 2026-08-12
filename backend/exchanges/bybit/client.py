from backend.exchanges.base import ExchangeClient
from pybit.unified_trading import HTTP

from backend.exchanges.models import Order, Side


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
        res = self.session.get_positions(category="linear", settleCoin="USDT")
        return res

    async def get_orders(self) -> list[Order]:
        res = self.session.get_open_orders(category="linear", settleCoin="USDT")
        return [
            Order(
                symbol=data["symbol"],
                side=Side.LONG if data["side"] == "Buy" else Side.SHORT
            )
            for data in res["result"]["list"]
        ]

    async def get_balance(self) -> float:
        res = self.session.get_wallet_balance(accountType="UNIFIED")
        return float(res["result"]["list"][0]["totalEquity"])

    async def close_position(self):
        pass

    async def cancel_order(self):
        pass


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import asyncio
    from pprint import pprint
    load_dotenv()

    client = ByBitClient(api_key=os.getenv("API_KEY_BYBIT"),
                         api_secret=os.getenv("API_SECRET_BYBIT"))

    pprint(asyncio.run(client.get_orders()))
