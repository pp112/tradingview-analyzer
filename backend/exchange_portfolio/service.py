import asyncio
import time
from typing import Awaitable, Callable

from sqlmodel import Session

from backend.exchange_portfolio.models import Portfolio
from backend.exchanges.base import ExchangeClient
from backend.signal_links.order_position_sync import sync_order_links_to_positions
from backend.storage.database import engine


class PortfolioService:
    """Сервис для работы с портфелем биржи."""

    def __init__(
        self, 
        client: ExchangeClient, 
        on_updated: Callable[[], Awaitable[None]] | None = None
    ):
        self._client = client
        self._on_updated = on_updated
        self._lock = asyncio.Lock()
        self._latest: Portfolio | None = None

    @property
    def latest(self) -> Portfolio | None:
        return self._latest

    async def sync(self) -> Portfolio:
        """
        Загружает снимок биржи, синхронизирует привязки ордеров
        с позициями в БД, сохраняет снимок и уведомляет подписчиков.
        """
        async with self._lock:
            portfolio = await self._fetch_snapshot()
            with Session(engine) as session, session.begin():
                sync_order_links_to_positions(
                    session, list(portfolio.orders), list(portfolio.positions)
                )
            self._latest = portfolio

        if self._on_updated is not None:
            await self._on_updated()
        return portfolio
    
    async def _fetch_snapshot(self) -> Portfolio:
        """
        Загружает текущее состояние (позиции, ордера, баланс).
        """
        positions, orders, balance = await asyncio.gather(
            self._client.get_positions(),
            self._client.get_orders(),
            self._client.get_balance(),
        )
        return Portfolio(
            positions=tuple(positions),
            orders=tuple(orders),
            balance=balance,
            updated_at=time.time(),
        )
