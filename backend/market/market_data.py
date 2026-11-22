import logging
import asyncio
from dataclasses import asdict

import pandas as pd

from backend.market import TradingViewWebSocket, fetch_tickers
from backend.models import Timeframe, Candle
from backend.utils import create_progress, to_display_symbol

logger = logging.getLogger(__name__)

CHUNK_SIZE = 20
WORKER_COUNT = 15
MAX_CONCURRENT_WS = 12

DEFAULT_MIN_CANDLES = 2250
MIN_CANDLES_BY_TIMEFRAME = {
    Timeframe.D1: 1700
}

CANDLE_COLUMNS = ["symbol", "timestamp", "open", "high", "low", "close", "volume"]

    
async def fetch_all_historical_candles(timeframe: Timeframe) -> pd.DataFrame:
    """
    Загружает исторические свечи для всех тикеров TradingView
    и возвращает единый DataFrame.

    Шаги:
    - получение списка тикеров (HTTP)
    - загрузка свечей чанками через WebSocket
    - сбор результатов в DataFrame  
    """
    tickers = list(await fetch_tickers())
    chunks = _chunk_list(tickers, CHUNK_SIZE)
    results = await _run_ws_pool(chunks, len(tickers), timeframe)

    return _to_dataframe(results)


async def _run_ws_pool(
    chunks: list[list[str]],
    total: int,
    timeframe: Timeframe
) -> dict[str, list[Candle]]:
    """
    Параллельно запускает WebSocket воркеры для загрузки данных.
    """
    queue = asyncio.Queue()
    for chunk in chunks:
        queue.put_nowait(chunk)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_WS)

    results: dict[str, list[Candle]] = {}
    lock = asyncio.Lock()

    progress = create_progress()
    task_id = progress.add_task(
        f"[cyan]Загрузка данных ({timeframe.label})",
        total=total
    )

    async def worker(worker_id: int):
        while True:
            try:
                chunk = queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            await asyncio.sleep(0.4 * worker_id)

            async with semaphore:
                try:
                    async with TradingViewWebSocket() as ws:

                        def update_progress():
                            progress.update(task_id, advance=1)

                        data = await ws.fetch_historical_batch(update_progress, chunk, timeframe)
                        filtered = _filter_by_candle_count(data, timeframe)

                        async with lock:
                            results.update(filtered)

                except Exception as e:
                    logger.error(f"Ошибка в WS worker {worker_id}: {e}")
    
    workers = [asyncio.create_task(worker(i)) for i in range(WORKER_COUNT)]

    with progress:
        await asyncio.gather(*workers)

    return results


def _to_dataframe(all_data: dict[str, list[Candle]]) -> pd.DataFrame:
    """
    Преобразует словарь {symbol: [Candle]} в единый DataFrame.
    """
    df_list = []

    for symbol, candles in all_data.items():
        df = pd.DataFrame.from_records(asdict(c) for c in candles)
        df["symbol"] = to_display_symbol(symbol)
        df_list.append(df)

    if not df_list:
        return pd.DataFrame(columns=CANDLE_COLUMNS)

    return pd.concat(df_list, ignore_index=True)


def _filter_by_candle_count(
    data: dict[str, list[Candle]],
    timeframe: Timeframe
) -> dict[str, list[Candle]]:
    min_candles = MIN_CANDLES_BY_TIMEFRAME.get(timeframe, DEFAULT_MIN_CANDLES)
    return {
        symbol: candles 
        for symbol, candles in data.items() 
        if len(candles) >= min_candles
    }


def _chunk_list(data: list[str], chunk_size: int) -> list[list[str]]:
    return [
        data[i:i + chunk_size]
        for i in range(0, len(data), chunk_size)
    ]
