import asyncio

from backend.exchanges.base import ExchangeClient
from backend.exchanges.models import Order, Position, Side
from backend.config import get_logger

from pybit.unified_trading import HTTP

logger = get_logger(__name__, "[BYBIT]")


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

    def _check_response(self, res: dict, action: str) -> dict | None:
        """Проверяет ответ Bybit."""
        ret_code = res.get("retCode")
        if ret_code != 0:
            ret_msg = res.get("retMsg", "неизвестная ошибка")
            logger.error(f"{action}: ошибка Bybit API ({ret_code}): {ret_msg}")
            return None
        return res

    async def get_orders(self) -> list[Order]:
        try:
            res = await asyncio.to_thread(
                self.session.get_open_orders, category="linear", settleCoin="USDT", orderFilter="Order"
            )
        except Exception as e:
            logger.error(f"Не удалось получить ордера (сетевая ошибка): {e}")
            return []

        res = self._check_response(res, "получение ордеров")
        if res is None:
            return []
        
        return [
            Order(
                id=data["orderId"],
                symbol=data["symbol"],
                side=Side.LONG if data["side"] == "Buy" else Side.SHORT,
            )
            for data in res["result"]["list"]
        ]

    async def get_positions(self) -> list[Position]:
        try:
            res = await asyncio.to_thread(
                self.session.get_positions, category="linear", settleCoin="USDT"
            )
        except Exception as e:
            logger.error(f"Не удалось получить позиции (сетевая ошибка): {e}")
            return []

        res = self._check_response(res, "получение позиций")
        if res is None:
            return []

        return [
            Position(
                symbol=data["symbol"],
                side=Side.LONG if data["side"] == "Buy" else Side.SHORT,
                pnl=round(float(data["unrealisedPnl"]), 2),
                pnlPct=(
                    round(float(data["unrealisedPnl"]) / float(data["positionIM"]) * 100, 2)
                    if float(data["positionIM"])
                    else 0.0
                ),
                size=float(data["size"]),
            )
            for data in res["result"]["list"]
        ]

    async def cancel_order(self, order: Order) -> bool:
        try:
            res = await asyncio.to_thread(
                self.session.cancel_order, category="linear", symbol=order.symbol, orderId=order.id
            )
        except Exception as e:
            logger.error(f"Не удалось отменить ордер {order.symbol} (сетевая ошибка): {e}")
            return False

        res = self._check_response(res, f"отмена ордера {order.symbol}")
        if res is None:
            return False

        logger.info(f"Ордер отменён: {order.symbol}")
        return True 

    async def close_position(self, position: Position) -> bool:
        try:
            res = await asyncio.to_thread(
                self.session.place_order,
                category="linear",
                symbol=position.symbol,
                side="Sell" if position.side == Side.LONG else "Buy",
                orderType="Market",
                qty=position.size,
                reduceOnly=True,
            )
        except Exception as e:
            logger.error(f"Не удалось закрыть позицию {position.symbol} (сетевая ошибка): {e}")
            return False

        res = self._check_response(res, f"закрытие позиции {position.symbol}")
        if res is None:
            return False

        logger.info(f"Позиция закрыта: {position.symbol}")
        return True

    async def get_balance(self) -> float | None:
        try:
            res = await asyncio.to_thread(
                self.session.get_wallet_balance, accountType="UNIFIED"
            )
        except Exception as e:
            logger.error(f"Не удалось получить баланс (сетевая ошибка): {e}")
            return None

        res = self._check_response(res, "получение баланса")
        if res is None:
            return None
        
        return float(res["result"]["list"][0]["totalEquity"])
