import asyncio
import json

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

clients: list[asyncio.Queue] = []


async def broadcast_signal(timeframe: str):
    message = json.dumps({"timeframe": timeframe})

    for queue in clients:
        await queue.put(("update", message))


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
                    event_type, msg = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"event: {event_type}\ndata: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: ping\n\n"
        
        finally:
            clients.remove(queue)

    return StreamingResponse(signal_update_stream(), media_type="text/event-stream")


@app.get("/signals")
def get_signals(tf: str):
    file_path = f"data/values/signals/signals_{tf}.json"
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def index():
    return FileResponse("web_copy/index.html")

app.mount("/", StaticFiles(directory="web_copy", html=True), name="web_copy")