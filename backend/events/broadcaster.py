import asyncio
from enum import StrEnum
import json

from backend.config.logging import get_logger
from backend.models.timeframe import Timeframe

logger = get_logger(__name__, "[EVENTS]")


class EventType(StrEnum):
    SIGNALS = "signals"
    PRICE_VOLUME = "price_volume"
    PORTFOLIO = "portfolio"


class Broadcaster:
    """
    Рассылает уведомления подписчикам SSE.
    """
    SSE_EVENT_NAME = "update"

    def __init__(self):
        self._subscribers: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._subscribers.add(queue)
        logger.info("Клиент подключился")
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        self._subscribers.discard(queue)

    async def signals_updated(self, timeframe: Timeframe):
        await self._publish({"type": EventType.SIGNALS, "timeframe": timeframe.label})

    async def price_volume_updated(self):
        await self._publish({"type": EventType.PRICE_VOLUME})

    async def portfolio_updated(self):
        await self._publish({"type": EventType.PORTFOLIO})

    async def _publish(self, message: dict):
        logger.info(f"Рассылка обновления: {message['type']}")
        json_message = json.dumps(message)
        for queue in list(self._subscribers):
            await queue.put((self.SSE_EVENT_NAME, json_message))