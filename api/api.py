import asyncio
import json

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from models import Timeframe


app = FastAPI()

clients: list[asyncio.Queue] = []


def broadcast_signal(timeframe: Timeframe):
    message = json.dumps({"timeframe": timeframe.label})

    for queue in clients:
        queue.put(("signals", message))


@app.get("/stream")
async def stream(request: Request):
    queue = asyncio.Queue()
    clients.append(queue)

    async def signal_update_stream():
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    event_type, msg = asyncio.wait_for(queue.get(), timeout=30)
                    yield f"event: {event_type}\ndata: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: ping\n\n"
        
        finally:
            clients.remove(queue)

    return StreamingResponse(signal_update_stream(), media_type="text/event-stream")


@app.get("/signals")
def get_signals(tf: str):
    # Сделать файл сигналов со всеми данными и путь до него
    ...