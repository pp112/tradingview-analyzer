from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.exchanges.base import ExchangeApiError
from backend.models import price_volume
from backend.api.routers import (
    initial_data,
    portfolio,
    price_volume,
    signal_links,
    signals,
    stream,
)

DEV_ORIGINS = [
    f"http://localhost:{port}"
    for port in range(5173, 5211)
] + [
    f"http://127.0.0.1:{port}"
    for port in range(5173, 5211)
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=DEV_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(signals.router)
app.include_router(price_volume.router)
app.include_router(initial_data.router)
app.include_router(portfolio.router)
app.include_router(stream.router)
app.include_router(signal_links.router)


@app.exception_handler(ExchangeApiError)
async def exchange_api_error_handler(request: Request, exc: ExchangeApiError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.get("/")
def index():
    return FileResponse("frontend/index.html")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")