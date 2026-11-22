import json
from pathlib import Path
import aiohttp

from backend.config import get_logger

logger = get_logger(__name__, "[HTTP]")

SCANNER_URL = "https://scanner.tradingview.com/crypto/scan?label-product=popup-screener-crypto-cex"
SCANNER_PAYLOAD_FILE = Path("backend/market/payloads/scanner.json")
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/"
}


async def fetch_tickers() -> dict[str, dict[str, float]]:
    """
    Возвращает все доступные крипто-тикеры TradingView и их цены.
    """
    payload = json.loads(SCANNER_PAYLOAD_FILE.read_text(encoding="utf-8"))

    async with aiohttp.ClientSession() as session:
        async with session.post(SCANNER_URL, headers=HEADERS, json=payload) as response:
            response.raise_for_status()
            raw = await response.json()

    tickers = _parse_tickers(raw)
    logger.info(f"Получено тикеров с данными: {len(tickers)}")
    return tickers


def _parse_tickers(data: dict) -> dict[str, dict[str, float]]:
    result = {}
    for item in data["data"]:
        if None in item["d"]:
            continue
        symbol_name = item["s"].split(":")[1]
        result[symbol_name] = {"price": item["d"][0]}
    return result