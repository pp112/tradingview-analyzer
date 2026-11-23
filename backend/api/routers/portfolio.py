from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_exchange_client, get_portfolio_service
from backend.config import get_logger
from backend.exchange_portfolio.service import PortfolioService
from backend.exchanges.base import ExchangeClient
from backend.schemas.common import ActionResponse
from backend.schemas.portfolio import OrderResponse, PortfolioResponse, PositionResponse


logger = get_logger(__name__, "[API]")

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(service: PortfolioService = Depends(get_portfolio_service)):
    """
    Возвращает последний снимок аккаунта: позиции, ордера, баланс и время снимка.
    """
    logger.info("Запрос открытых позиций и ордеров")
    portfolio = service.latest
    if portfolio is None:
        return PortfolioResponse(
            positions=[], orders=[], balance=None, updated_at=None
        )
    return PortfolioResponse(
        orders=[
            OrderResponse.model_validate(order, from_attributes=True)
            for order in portfolio.orders
        ],
        positions=[
            PositionResponse.model_validate(position, from_attributes=True)
            for position in portfolio.positions
        ],
        balance=portfolio.balance,
        updated_at=int(portfolio.updated_at * 1000),
    )


@router.post("/orders/{exchange_order_id}/cancel", response_model=ActionResponse)
async def cancel_order(
    exchange_order_id: str, 
    client: ExchangeClient = Depends(get_exchange_client),
):
    """
    Отменяет открытый ордер по его ID.
    """
    orders = await client.get_orders()
    order = next((o for o in orders if o.exchange_order_id == exchange_order_id), None)
    if order is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")

    success = await client.cancel_order(order)
    if not success:
        raise HTTPException(status_code=502, detail="Не удалось отменить ордер")

    return ActionResponse(success=True)


@router.post("/positions/close", response_model=ActionResponse)
async def close_position(
    symbol: str, 
    client: ExchangeClient = Depends(get_exchange_client),
):
    """
    Закрывает открытую позицию по символу.
    """
    positions = await client.get_positions()
    position = next((p for p in positions if p.symbol == symbol), None)
    if position is None:
        raise HTTPException(status_code=404, detail="Позиция не найдена")

    success = await client.close_position(position)
    if not success:
        raise HTTPException(status_code=502, detail="Не удалось закрыть позицию")

    return ActionResponse(success=True)
