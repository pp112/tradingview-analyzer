"""
CryptoScope API — FastAPI
Запуск: uvicorn api:app --host 0.0.0.0 --port 8000 --reload

Интегрируется в существующий main.py:
    from api import app as dashboard_app
    import uvicorn
    # запустить рядом с планировщиком:
    asyncio.create_task(uvicorn.Server(uvicorn.Config(dashboard_app, host="0.0.0.0", port=8000)).serve())
"""

import json
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CryptoScope API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path("data")

TIMEFRAME_LABELS = {
    "15m": "15m",
    "30m": "30m",
    "1h":  "1h",
    "4h":  "4h",
    "1d":  "1d",
}

SIGNAL_MAP = {
    "RSI_OVERBOUGHT":  {"indicator": "RSI",     "direction": "ВНИЗ", "bull": False},
    "RSI_OVERSOLD":    {"indicator": "RSI",     "direction": "ВВЕРХ","bull": True},
    "MACD_BULLISH":    {"indicator": "MACD",    "direction": "ВВЕРХ","bull": True},
    "MACD_BEARISH":    {"indicator": "MACD",    "direction": "ВНИЗ", "bull": False},
    "EMA_SMA_BULLISH": {"indicator": "EMA/SMA", "direction": "ВВЕРХ","bull": True},
    "EMA_SMA_BEARISH": {"indicator": "EMA/SMA", "direction": "ВНИЗ", "bull": False},
}


def _load_json(path: Path) -> dict | list | None:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def _file_age_minutes(path: Path) -> int | None:
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return int((datetime.now() - mtime).total_seconds() / 60)


# ── Serve static dashboard ──────────────────────────────────────────────────────

@app.get("/")
async def index():
    return FileResponse("dashboard/index.html")

app.mount("/dashboard", StaticFiles(directory="dashboard"), name="dashboard")


# ── API endpoints ───────────────────────────────────────────────────────────────

@app.get("/api/status")
async def status():
    """Статус обновлений по таймфреймам"""
    result = {}
    for tf in TIMEFRAME_LABELS.values():
        sig_path = BASE / "values" / "signals" / f"signals_{tf}.json"
        age = _file_age_minutes(sig_path)
        result[tf] = {
            "updated_minutes_ago": age,
            "has_data": sig_path.exists(),
        }
    return {"timeframes": result, "server_time": datetime.now().isoformat()}


@app.get("/api/signals/{timeframe}")
async def get_signals(timeframe: str):
    """Сигналы + значения индикаторов для таймфрейма"""
    tf = TIMEFRAME_LABELS.get(timeframe.lower())
    if not tf:
        return {"error": "unknown timeframe", "signals": []}

    signals = _load_json(BASE / "values" / "signals" / f"signals_{tf}.json") or []
    indicators = _load_json(BASE / "values" / "indicators" / f"values_{tf}.json") or {}

    rows = []
    seen = set()

    for s in signals:
        sym = s["symbol"]
        if sym in seen:
            continue
        seen.add(sym)

        meta = SIGNAL_MAP.get(s["signal"], {"indicator": "—", "direction": "—", "bull": None})
        ind = indicators.get(sym, {})

        rsi = ind.get("rsi")
        macd_block = ind.get("macd") or {}
        curr_macd = macd_block.get("curr") or {}
        ema = ind.get("ema") or [None, None]
        sma = ind.get("sma") or [None, None]
        vol = ind.get("volume") or {}

        macd_diff = None
        if curr_macd.get("MACD") is not None and curr_macd.get("MACD_signal") is not None:
            base = abs(curr_macd["MACD_signal"]) or 1e-9
            macd_diff = round(abs(curr_macd["MACD"] - curr_macd["MACD_signal"]) / base, 4)

        ema_sma_str = "—"
        if ema[1] and sma[1]:
            ema_sma_str = "EMA > SMA" if ema[1] > sma[1] else "EMA < SMA"

        rows.append({
            "symbol":     sym,
            "signal":     s["signal"],
            "indicator":  meta["indicator"],
            "direction":  meta["direction"],
            "bull":       meta["bull"],
            "rsi":        rsi,
            "macd_diff":  macd_diff,
            "ema_sma":    ema_sma_str,
            "vol_ratio":  round(vol.get("ratio", 0), 2),
            "timeframe":  tf,
        })

    age = _file_age_minutes(BASE / "values" / "signals" / f"signals_{tf}.json")
    return {"timeframe": tf, "count": len(rows), "updated_minutes_ago": age, "signals": rows}


@app.get("/api/correlations")
async def get_correlations():
    """Корреляции всех активов с BTC"""
    data = _load_json(BASE / "values" / "correlations" / "correlations.json") or {}
    items = [{"symbol": k, "corr": v} for k, v in data.items()]
    items.sort(key=lambda x: x["corr"], reverse=True)
    return {"count": len(items), "correlations": items}


@app.get("/api/reports/{timeframe}")
async def get_reports(timeframe: str):
    """Список доступных текстовых отчётов"""
    tf = TIMEFRAME_LABELS.get(timeframe.lower(), timeframe)
    base = BASE / "reports" / tf
    if not base.exists():
        return {"reports": []}

    reports = []
    for txt in base.rglob("*.txt"):
        reports.append({
            "path":  str(txt.relative_to(BASE / "reports")),
            "group": txt.parent.name,
            "name":  txt.stem,
        })
    return {"reports": reports}


@app.get("/api/reports/{timeframe}/{group}/{name}")
async def get_report_content(timeframe: str, group: str, name: str):
    """Содержимое конкретного отчёта"""
    tf = TIMEFRAME_LABELS.get(timeframe.lower(), timeframe)
    path = BASE / "reports" / tf / group / f"{name}.txt"
    if not path.exists():
        return {"error": "not found", "lines": []}
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return {"lines": lines}


@app.get("/api/indicators/{timeframe}/{symbol}")
async def get_indicator(timeframe: str, symbol: str):
    """Детальные индикаторы для конкретного символа"""
    tf = TIMEFRAME_LABELS.get(timeframe.lower())
    if not tf:
        return {"error": "unknown timeframe"}
    indicators = _load_json(BASE / "values" / "indicators" / f"values_{tf}.json") or {}
    data = indicators.get(symbol)
    if not data:
        return {"error": "symbol not found"}
    return {"symbol": symbol, "timeframe": tf, "indicators": data}
