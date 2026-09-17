import asyncio
import json
from pathlib import Path
from typing import TypedDict, Required, NotRequired

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import TypeAdapter

from backend.api.dependencies import get_bybit_client
from backend.api.signal_links import router as signal_links_router
from backend.config import get_logger
from backend.exchanges.base import ExchangeApiError, ExchangeClient
from backend.schemas.signals import SignalResponse
from backend.schemas.price_volume import PriceVolumeResponse
from backend.schemas.positions import PositionResponse
from backend.schemas.orders import OrderResponse
from backend.schemas.linked_values import CurrentIndicatorValueResponse
from backend.schemas.initial_data import InitialDataResponse
from backend.schemas.balance import BalanceResponse
from backend.schemas.common import ActionResponse


logger = get_logger(__name__, "[API]")


app = FastAPI()


BASE_DIR = Path("backend/data/values")

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
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(signal_links_router)


clients: list[asyncio.Queue] = []

class BroadcastMessage(TypedDict):
    type: Required[str]
    timeframe: NotRequired[str]

async def broadcast(message: BroadcastMessage):
    """
    Рассылает уведомление об обновлении данных подключённым клиентам.
    """
    json_message = json.dumps(message)
    logger.info(f"Рассылка обновления: {message['type']}")

    for queue in clients:
        await queue.put(("update", json_message))


@app.exception_handler(ExchangeApiError)
async def exchange_api_error_handler(request: Request, exc: ExchangeApiError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.get("/stream")
async def stream(request: Request):
    """
    SSE эндпоинт — держит соединение открытым и отправляет события клиенту.
    """
    queue = asyncio.Queue()
    clients.append(queue)
    logger.info(f"Клиент подключился")

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
            clients.remove(queue)

    return StreamingResponse(signal_update_stream(), media_type="text/event-stream")


@app.get("/signals", response_model=list[SignalResponse])
def get_signals(tf: str):
    """
    Возвращает сигналы для указанного таймфрейма из JSON файла.
    """
    logger.info(f"Запрос сигналов: {tf}")
    path = BASE_DIR / "signals" / f"signals_{tf}.json"
    json_data = path.read_text(encoding="utf-8")
    return SIGNALS_ADAPTER.validate_json(json_data)
    

@app.get("/price_volume", response_model=list[PriceVolumeResponse])
def get_price_volume():
    """
    Возвращает последние изменения цен и объёмов.
    """
    logger.info("Запрос изменений цен и объёмов")
    path = BASE_DIR / "price_vol_changes" / "price_vol_changes.json"
    json_data = path.read_text(encoding="utf-8")
    return PRICE_VOLUME_ADAPTER.validate_json(json_data)
    

@app.get("/initial_data", response_model=InitialDataResponse)
def get_initial_data():
    """
    Возвращает все актуальные данные для клиента при первом подключении:
    - сигналы по таймфреймам
    - изменения цен и объёмов
    """
    signals: dict[str, list[SignalResponse]] = {}

    signals_dir = BASE_DIR / "signals"
    for file_path in signals_dir.glob("signals_*.json"):
        tf_label = file_path.stem.removeprefix("signals_")
        json_data = file_path.read_text(encoding="utf-8")
        signals[tf_label] = SIGNALS_ADAPTER.validate_json(json_data)

    price_changes = None
    price_changes_path = BASE_DIR / "price_vol_changes" / "price_vol_changes.json"
    if price_changes_path.exists():
        json_data = price_changes_path.read_text(encoding="utf-8")
        price_changes = PRICE_VOLUME_ADAPTER.validate_json(json_data)

    return InitialDataResponse(signals=signals, price_changes=price_changes)

@app.get("/positions", response_model=list[PositionResponse])
async def get_positions(client: ExchangeClient = Depends(get_bybit_client)):
    """
    Возвращает список открытых позиций.
    """
    logger.info("Запрос открытых позиций")
    positions = await client.get_positions()
    return [
        PositionResponse.model_validate(position, from_attributes=True)
        for position in positions
    ]


@app.get("/orders", response_model=list[OrderResponse])
async def get_orders(client: ExchangeClient = Depends(get_bybit_client)):
    """
    Возвращает список открытых ордеров.
    """
    logger.info("Запрос открытых ордеров")
    orders = client.get_orders()
    return [
        OrderResponse.model_validate(order, from_attributes=True)
        for order in orders
    ]


@app.get("/balance", response_model=BalanceResponse)
async def get_balance(client: ExchangeClient = Depends(get_bybit_client)):
    """
    Возвращает баланс аккаунта.
    """
    logger.info("Запрос баланса")
    return BalanceResponse(balance=await client.get_balance())


@app.post("/orders/{exchange_order_id}/cancel", response_model=ActionResponse)
async def cancel_order(
    exchange_order_id: str, 
    client: ExchangeClient = Depends(get_bybit_client)
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
async def close_position(symbol: str, client: ExchangeClient = Depends(get_bybit_client)):
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
async def get_linked_signal_values(tf: str):
    """
    Возвращает текущие значения индикаторов для привязанных сигналов
    указанного таймфрейма.
    """
    path = BASE_DIR / "linked_values" / f"linked_values_{tf}.json"
    if not path.exists():
        return []
    json_data = path.read_text(encoding="utf-8")
    return LINKED_VALUES_ADAPTER.validate_json(json_data)


@app.get("/")
def index():
    return FileResponse("frontend/index.html")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")