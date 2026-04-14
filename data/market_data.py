import os
import logging
import json
import asyncio
import pandas as pd
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s",
)
from data.http_client import TradingViewHttpClient
from data.websocket_client import TradingViewWebSocket, Timeframe, TOHLC

logger = logging.getLogger(__name__)


class MarketDataClient:
    """
    Класс для получения исторических данных и сохранения их в json и parquet.

    Объединяет работу TradingViewHttpClient и TradingViewWebSocket
    """
    def __init__(self):
        self.http_client = TradingViewHttpClient()
        self.ws_client = TradingViewWebSocket()
        
    async def get_all_historical_ohlc(
        self,
        timeframe: Timeframe = Timeframe.H1
    ) -> None:
        chunk_size = 20

        tickers = await self.http_client.get_all_tickers()
        chunks = self._chunk_list(tickers, chunk_size)

        results = await self._run_ws_pool(chunks, timeframe)

        self._save_to_files(results, timeframe)

    async def _run_ws_pool(
        self,
        chunks: list[list[str]],
        timeframe: Timeframe
    ) -> dict[str, list[TOHLC]]:
        worker_count = 15
        max_concurrent_ws = 15

        queue = asyncio.Queue()
        for chunk in chunks:
            queue.put_nowait(chunk)

        semaphore = asyncio.Semaphore(max_concurrent_ws)

        results: dict[str, list[TOHLC]] = {}
        lock = asyncio.Lock()

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
                            data = await ws.get_historical_batch(chunk, timeframe)

                            async with lock:
                                results.update(data)

                    except Exception as e:
                        logger.error(f"Ошибка в WS worker {worker_id}: {e}")

        workers = [
            asyncio.create_task(worker(i))
            for i in range(worker_count)
        ]

        await asyncio.gather(*workers)

        return results
    
    def _save_to_files(
        self, 
        all_data: dict[str, list[dict]],
        timeframe: Timeframe
    ):
        save_path = "data/historical_data"
        filename = f"historical_data_{timeframe.value}"

        os.makedirs(save_path, exist_ok=True)

        df_list = []
        for symbol, series in all_data.items():
            df = pd.DataFrame(series)
            df["symbol"] = symbol
            df_list.append(df)

        if df_list:
            full_df = pd.concat(df_list, ignore_index=True)
            full_df.to_parquet(
                f"{save_path}/{filename}.parquet",
                engine="pyarrow"
            )

        with open(f"{save_path}/{filename}.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

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
    data = asyncio.run(market_client.get_all_historical_ohlc())
    print(f"Затрачено: {time.time() - start}")
