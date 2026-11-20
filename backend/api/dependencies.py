from fastapi import Request

from backend.events.broadcaster import Broadcaster
from backend.exchange_portfolio.service import PortfolioService
from backend.exchanges.base import ExchangeClient


def get_exchange_client(request: Request) -> ExchangeClient:
    return request.app.state.exchange_client


def get_portfolio_service(request: Request) -> PortfolioService:
    return request.app.state.portfolio_service


def get_broadcaster(request: Request) -> Broadcaster:
    return request.app.state.broadcaster