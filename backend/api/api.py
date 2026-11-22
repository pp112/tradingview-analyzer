import asyncio

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import TypeAdapter

from backend.api.dependencies import (
    get_broadcaster,
    get_exchange_client,
    get_portfolio_service,
)
from backend.api.signal_links import router as signal_links_router
from backend.config import get_logger
from backend.events.broadcaster import Broadcaster
from backend.exchange_portfolio.service import PortfolioService
from backend.exchanges.base import ExchangeApiError, ExchangeClient
from backend.schemas.signals import SignalResponse
from backend.schemas.price_volume import PriceVolumeResponse
from backend.schemas.portfolio import OrderResponse, PositionResponse, PortfolioResponse
from backend.schemas.linked_values import CurrentIndicatorValueResponse
from backend.schemas.initial_data import InitialDataResponse
from backend.schemas.common import ActionResponse
from backend.storage.paths import (
    LINKED_VALUES_FILE, 
    PRICE_VOLUME_FILE,
    SIGNALS_DIR,
    signals_file,
)
from backend.storage.writer import read_json


logger = get_logger(__name__, "[API]")


app = FastAPI()


SIGNALS_ADAPTER = TypeAdapter(list[SignalResponse])
PRICE_VOLUME_ADAPTER = TypeAdapter(list[PriceVolumeResponse])
LINKED_VALUES_ADAPTER = TypeAdapter(list[CurrentIndicatorValueResponse])


DEV_ORIGINS = [
    f"http://localhost:{port}"
    for port in range(5173, 5211)
] + [
    f"http://127.0.0.1:{port}"
    for port in range(5173, 5211)
]
app.add_middleware(
    CORSMiddleware, 
    allow_origins=DEV_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(signal_links_router)


@app.exception_handler(ExchangeApiError)
async def exchange_api_error_handler(exc: ExchangeApiError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.get("/stream")
async def stream(
    request: Request, 
    broadcaster: Broadcaster = Depends(get_broadcaster)
):
    """
    SSE эндпоинт — держит соединение открытым и отправляет события клиенту.
    """
    queue = broadcaster.subscribe()

    async def signal_update_stream():
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    event_type, msg = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"event: {event_type}\ndata: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: ping\n\n"
        
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(signal_update_stream(), media_type="text/event-stream")


@app.get("/signals", response_model=list[SignalResponse])
def get_signals(tf: str):
    """
    Возвращает сигналы для указанного таймфрейма из JSON файла.
    """
    logger.info(f"Запрос сигналов: {tf}")
    path = signals_file(tf)
    json_data = path.read_text(encoding="utf-8")
    return SIGNALS_ADAPTER.validate_json(json_data)
    

@app.get("/price_volume", response_model=list[PriceVolumeResponse])
def get_price_volume():
    """
    Возвращает последние изменения цен и объёмов.
    """
    logger.info("Запрос изменений цен и объёмов")
    if not PRICE_VOLUME_FILE.exists():
        return []
    json_data = PRICE_VOLUME_FILE.read_text(encoding="utf-8")
    return PRICE_VOLUME_ADAPTER.validate_json(json_data)
    

@app.get("/initial_data", response_model=InitialDataResponse)
def get_initial_data():
    """
    Возвращает все актуальные данные для клиента при первом подключении:
    - сигналы по таймфреймам
    - изменения цен и объёмов
    """
    signals: dict[str, list[SignalResponse]] = {}

    for file_path in SIGNALS_DIR.glob("signals_*.json"):
        tf_label = file_path.stem.removeprefix("signals_")
        json_data = file_path.read_text(encoding="utf-8")
        signals[tf_label] = SIGNALS_ADAPTER.validate_json(json_data)

    price_changes = []
    if PRICE_VOLUME_FILE.exists():
        json_data = PRICE_VOLUME_FILE.read_text(encoding="utf-8")
        price_changes = PRICE_VOLUME_ADAPTER.validate_json(json_data)

    return InitialDataResponse(signals=signals, price_changes=price_changes)


@app.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(service: PortfolioService = Depends(get_portfolio_service)):
    """
    Возвращает открытые ордера и позиции.
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


@app.post("/orders/{exchange_order_id}/cancel", response_model=ActionResponse)
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


@app.post("/positions/close", response_model=ActionResponse)
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


@app.get("/linked-signal-values", response_model=list[CurrentIndicatorValueResponse])
def get_linked_signal_values(tf: str):
    """
    Возвращает текущие значения индикаторов для привязанных сигналов
    указанного таймфрейма.
    """
    data = read_json(LINKED_VALUES_FILE, default={})
    return LINKED_VALUES_ADAPTER.validate_python(data.get(tf, []))


@app.get("/")
def index():
    return FileResponse("frontend/index.html")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")