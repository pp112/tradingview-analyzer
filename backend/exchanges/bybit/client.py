import asyncio

from backend.exchanges.base import ExchangeApiError, ExchangeClient
from backend.exchanges.models import Order, Position, Side
from backend.config import get_logger
from backend.utils import to_display_symbol, to_exchange_symbol

from pybit.unified_trading import HTTP

logger = get_logger(__name__, "[BYBIT]")


def _calc_target_progress_pct(
    side: Side,
    pnl: float,
    entry_price: float,
    mark_price: float,
    take_profit: float | None,
    stop_loss: float | None,
) -> float | None:
    """
    Возвращает % прогресса к TP (если позиция в плюсе) или к SL (если в минусе).
    None, если соответствующий уровень не задан.
    """
    is_profit = pnl >= 0

    if is_profit:
        if not take_profit:
            return None
        if side == side.LONG:
            distance_total = take_profit - entry_price
            distance_covered = mark_price - entry_price
        else:
            distance_total = entry_price - take_profit
            distance_covered = entry_price - mark_price
        if distance_total <= 0:
            return None
        return round(distance_covered / distance_total * 100, 2)
    else:
        if not stop_loss:
            return None
        if side == side.LONG:
            distance_total = entry_price - stop_loss
            distance_covered = entry_price - mark_price
        else:
            distance_total = stop_loss - entry_price
            distance_covered = mark_price - entry_price
        if distance_total <= 0:
            return None
        return round(-(distance_covered / distance_total * 100), 2)


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

    def _check_response(self, res: dict, action: str) -> dict:
        """Проверяет ответ Bybit."""
        ret_code = res.get("retCode")
        if ret_code != 0:
            ret_msg = res.get("retMsg", "неизвестная ошибка")
            logger.error(f"{action}: ошибка Bybit API ({ret_code}): {ret_msg}")
            raise ExchangeApiError(f"{action}: {ret_msg}")
        return res

    async def get_orders(self) -> list[Order]:
        try:
            res = await asyncio.to_thread(
                self.session.get_open_orders, category="linear", settleCoin="USDT", orderFilter="Order"
            )
        except Exception as e:
            logger.error(f"Не удалось получить ордера (сетевая ошибка): {e}")
            raise ExchangeApiError("Не удалось получить ордера") from e

        res = self._check_response(res, "получение ордеров")
        
        return [
            Order(
                id=data["orderId"],
                symbol=to_display_symbol(data["symbol"]),
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
            raise ExchangeApiError("Не удалось получить позиции") from e

        res = self._check_response(res, "получение позиций")

        positions = []
        for data in res["result"]["list"]:
            side = Side.LONG if data["side"] == "Buy" else Side.SHORT
            pnl = round(float(data["unrealisedPnl"]), 2)
            entry_price = float(data["avgPrice"])
            mark_price = float(data["markPrice"])
            take_profit = float(data.get("takeProfit")) if data.get("takeProfit") else None
            stop_loss = float(data.get("stopLoss")) if data.get("stopLoss") else None

            pnl_pct = _calc_target_progress_pct(
                side=side,
                pnl=pnl,
                entry_price=entry_price,
                mark_price=mark_price,
                take_profit=take_profit,
                stop_loss=stop_loss
            )

            positions.append(
                Position(
                    symbol=to_display_symbol(data["symbol"]),
                    side=side,
                    pnl=pnl,
                    pnlPct=pnl_pct,
                    size=float(data["size"]),
                )
            )

        return positions
        
    async def cancel_order(self, order: Order) -> bool:
        try:
            res = await asyncio.to_thread(
                self.session.cancel_order, 
                category="linear", 
                symbol=to_exchange_symbol(order.symbol), 
                orderId=order.id
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
                symbol=to_exchange_symbol(position.symbol),
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
            raise ExchangeApiError("Не удалось получить баланс") from e

        res = self._check_response(res, "получение баланса")
        
        return float(res["result"]["list"][0]["totalEquity"])
