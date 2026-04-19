import logging
import asyncio

import pandas as pd

from market import TradingViewHttpClient, TradingViewWebSocket
from models.timeframe import Timeframe
from models.tohlc import TOHLC
from utils import create_progress

logger = logging.getLogger(__name__)


class MarketDataClient:
    """
    Клиент для загрузки исторических данных.

    Выполняет:
    - получение списка тикеров (HTTP)
    - загрузку TOHLC данных (WebSocket)
    - сбор результатов в DataFrame
    """
    def __init__(self):
        self.http_client = TradingViewHttpClient()
        self.ws_client = TradingViewWebSocket()
        
    async def fetch_all_historical_tohlc(self, timeframe: Timeframe) -> pd.DataFrame:
        """
        Загружает исторические данные для всех тикеров и сохраняет их локально.
        """
        chunk_size = 20

        tickers = await self.http_client.fetch_all_tickers()
        chunks = MarketDataClient._chunk_list(tickers, chunk_size)
        results = await self._run_ws_pool(chunks, len(tickers), timeframe)

        return self._to_dataframe(results)

    async def _run_ws_pool(
        self,
        chunks: list[list[str]],
        total: int,
        timeframe: Timeframe
    ) -> dict[str, list[TOHLC]]:
        """
        Параллельно запускает WebSocket воркеры для загрузки данных.
        """
        worker_count = 15
        max_concurrent_ws = 12

        queue = asyncio.Queue()
        for chunk in chunks:
            queue.put_nowait(chunk)

        semaphore = asyncio.Semaphore(max_concurrent_ws)

        results: dict[str, list[TOHLC]] = {}
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

                            async with lock:
                                results.update(data)

                    except Exception as e:
                        logger.error(f"Ошибка в WS worker {worker_id}: {e}")
        
        workers = [
            asyncio.create_task(worker(i))
            for i in range(worker_count)
        ]

        with progress:
            await asyncio.gather(*workers)

        return results
    
    def _to_dataframe(self, all_data):
        """
        Преобразует словарь TOHLC данных в DataFrame.
        """
        df_list = []

        for symbol, series in all_data.items():
            df = pd.DataFrame(series)
            df["symbol"] = symbol
            df_list.append(df)

        if not df_list:
            return pd.DataFrame()

        return pd.concat(df_list, ignore_index=True)

    @staticmethod
    def _chunk_list(data: list[str], chunk_size: int) -> list[list[str]]:
        return [
            data[i:i + chunk_size]
            for i in range(0, len(data), chunk_size)
        ]
    
    
if __name__ == "__main__":
    market_client = MarketDataClient()
    import time
    start = time.time()
    data = asyncio.run(market_client.fetch_all_historical_tohlc())
    print(f"Затрачено: {time.time() - start}")
