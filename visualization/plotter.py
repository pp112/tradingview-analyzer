import logging
import os
import pandas as pd
import mplfinance as mpf
from data.websocket_client import Timeframe

logger = logging.getLogger(__name__)


class MarketPlotter:
    def _load_data(self, timeframe: Timeframe) -> pd.DataFrame:
        data_path = f"data/results/historical_data_{timeframe.value}.parquet"
        return pd.read_parquet(data_path)
    
    def _prepare_data(self, symbol: str, timeframe: Timeframe) -> pd.DataFrame:
        df = self._load_data(timeframe)

        df = df[df["symbol"] == symbol].copy()

        if df.empty:
            return None

        df["Date"] = pd.to_datetime(df["Timestamp"], unit="s")
        df.set_index("Date", inplace=True)

        return df
    
    def plot_candles(
        self, 
        symbol: str = "BTCUSDT.P", 
        timeframe: Timeframe = Timeframe.H1
    ) -> str:
        df = self._prepare_data(symbol, timeframe)
        if df is None:
            logger.error(f"Нет данных для {symbol}")
            return
        
        save_folder = "visualization/plots/"
        os.makedirs(save_folder, exist_ok=True)
        save_path = f"{save_folder}/{symbol}_{timeframe.value}.jpg"
        mpf.plot(
            df, 
            type="candle", 
            style="charles",
            title=symbol, 
            volume=False,
            figscale=(15, 8),
            savefig=dict(
                fname=save_path,
                dpi=300
            )
        )
        
        logger.info(f"Графика {symbol}_{timeframe.value} успешно сохранен в {save_path}")
        
        return save_path 


if __name__ == "__main__":
    plotter = MarketPlotter()
    img = plotter.plot_candles()
 