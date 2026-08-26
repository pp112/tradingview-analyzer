import asyncio
import json
from pathlib import Path
from typing import TypedDict, Required, NotRequired

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.dependencies import get_bybit_client
from backend.config import get_logger
from backend.exchanges.base import ExchangeClient
from backend.exchanges.models import PositionOut
from backend.api.signal_links import router as signal_links_router


logger = get_logger(__name__, "[API]")


app = FastAPI()
app.include_router(signal_links_router)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:5173"]
)

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


@app.get("/signals")
def get_signals(tf: str):
    """
    Возвращает сигналы для указанного таймфрейма из JSON файла.
    """
    logger.info(f"Запрос сигналов: {tf}")
    path = Path("backend/data/values/signals") / f"signals_{tf}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
    

@app.get("/price_volume")
def get_price_volume():
    """
    Возвращает последние изменения цен и объёмов.
    """
    logger.info("Запрос изменений цен и объёмов")
    path = Path("backend/data/values/price_vol_changes/price_vol_changes.json")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
    

@app.get("/initial_data")
def get_initial_data():
    """
    Возвращает все актуальные данные для клиента при первом подключении:
    - сигналы по таймфреймам
    - изменения цен и объёмов
    """
    signals = {}
    for file_path in Path("backend/data/values/signals").glob("signals_*.json"):
        tf_label = file_path.stem.replace("signals_", "")
        signals[tf_label] = json.loads(file_path.read_text(encoding="utf-8"))

    price_changes_path = Path("backend/data/values/price_vol_changes/price_vol_changes.json")
    if price_changes_path.exists():
        price_changes = json.loads(price_changes_path.read_text(encoding="utf-8"))
    else:
        price_changes = None

    return {
        "signals": signals,
        "price_changes": price_changes
    }


@app.get("/positions", response_model=list[PositionOut])
async def get_positions(client: ExchangeClient = Depends(get_bybit_client)):
    """
    Возвращает список открытых позиций.
    """
    logger.info("Запрос открытых позиций")
    return await client.get_positions()


@app.get("/orders")
async def get_orders(client: ExchangeClient = Depends(get_bybit_client)):
    """
    Возвращает список открытых ордеров.
    """
    logger.info("Запрос открытых ордеров")
    return await client.get_orders()


@app.get("/balance")
async def get_balance(client: ExchangeClient = Depends(get_bybit_client)):
    """
    Возвращает баланс аккаунта.
    """
    logger.info("Запрос баланса")
    return {"balance": await client.get_balance()}


@app.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str, client: ExchangeClient = Depends(get_bybit_client)):
    """
    Отменяет открытый ордер по его ID.
    """
    orders = await client.get_orders()
    order = next((o for o in orders if o.id == order_id), None)

    if order is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")

    success = await client.cancel_order(order)
    if not success:
        raise HTTPException(status_code=502, detail="Не удалось отменить ордер")

    return {"success": True}


@app.post("/positions/{symbol}/close")
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

    return {"success": True}


@app.get("/")
def index():
    return FileResponse("frontend/index.html")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")