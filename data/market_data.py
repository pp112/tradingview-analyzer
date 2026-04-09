import os
import json
import pandas as pd

from http_client import TradingViewHttpClient
from websocket_client import TradingViewWebSocket, Timeframe, TOHLC

class MarketDataClient:
    def __init__(self):
        self.http_client = TradingViewHttpClient()
        self.ws_client = TradingViewWebSocket()

    def get_all_tickers(self) -> list[str]:
        return self.http_client.get_all_tickers()
    
    def get_historical_ohlc(
        self, 
        symbol: str, 
        timeframe: Timeframe = Timeframe.H1
    ) -> list[TOHLC] | None:
        """
        Получить исторические TOHLC-бары для одного тикера.
        """
        with self.ws_client as ws:
            return ws.get_historical_bars(symbol, timeframe)
        
    def get_all_historical_ohlc(
        self, 
        timeframe: Timeframe = Timeframe.H1    
    ) -> dict[str, list[dict]] | None:
        """
        Получить исторические TOHLC-бары для всех тикеров
        """
        tickers = self.get_all_tickers()
        all_data = {}

        with self.ws_client as ws:
            for symbol in tickers:
                series = ws.get_historical_bars(symbol, timeframe)
                if series:
                    all_data[symbol] = series
        
        self._save_to_files(all_data, timeframe)
        return all_data
    
    def _save_to_files(
        self, 
        all_data: dict[str, list[dict]],
        timeframe: Timeframe
    ):
        save_path = "data/results"
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
    
    
if __name__ == "__main__":
    market_client = MarketDataClient()
    import time
    start = time.time()
    data = market_client.get_all_historical_ohlc()
    print(f"Затрачено: {time.time() - start}")

    import json
    with open("data/result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)