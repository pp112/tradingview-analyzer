import asyncio

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from backend.api.dependencies import get_broadcaster
from backend.events.broadcaster import Broadcaster


router = APIRouter(tags=["stream"])


@router.get("/stream")
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