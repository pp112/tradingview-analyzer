import asyncio
import json
from pathlib import Path
from typing import TypedDict, Required, NotRequired

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config import get_logger

logger = get_logger(__name__, "[API]")


app = FastAPI()

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
    path = Path("data/values/signals") / f"signals_{tf}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
    

@app.get("/price_volume")
def get_price_volume():
    """
    Возвращает последние изменения цен и объёмов.
    """
    logger.info("Запрос изменений цен и объёмов")
    path = Path("data/values/price_vol_changes/price_vol_changes.json")
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
    for file_path in Path("data/values/signals").glob("signals_*.json"):
        tf_label = file_path.stem.replace("signals_", "")
        signals[tf_label] = json.loads(file_path.read_text(encoding="utf-8"))

    price_changes_path = Path("data/values/price_vol_changes/price_vol_changes.json")
    if price_changes_path.exists():
        price_changes = json.loads(price_changes_path.read_text(encoding="utf-8"))
    else:
        price_changes = None

    return {
        "signals": signals,
        "price_changes": price_changes
    }


@app.get("/")
def index():
    return FileResponse("web/index.html")

app.mount("/", StaticFiles(directory="web", html=True), name="web")