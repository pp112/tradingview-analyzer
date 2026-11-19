from dataclasses import dataclass

from backend.exchanges.models import Position, Order


@dataclass(frozen=True)
class Portfolio:
    """Снимок биржи: позиции, ордера и баланс"""
    positions: tuple[Position, ...]
    orders: tuple[Order, ...]
    balance: float | None
    updated_at: float