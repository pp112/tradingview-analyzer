import logging
import os
import warnings

import pandas as pd
import mplfinance as mpf

from data.websocket_client import Timeframe

logger = logging.getLogger(__name__)


class MarketPlotter:
    """
    Класс для построения свечных графиков криптовалют с техническими индикаторами.

    Поддерживает:
    - EMA / SMA
    - RSI
    - MACD

    Графики сохраняются в виде изображений (jpg).
    """

    def plot_candles(
        self, 
        symbol: str = "BTCUSDT.P", 
        timeframe: Timeframe = Timeframe.H1,
        ema_sma: bool = False,
        rsi: bool = False,
        macd: bool = False
    ) -> str:
        df = self._prepare_data(symbol, timeframe)
        if df is None:
            logger.error(f"Нет данных для {symbol}")
            return
        
        save_folder = "visualization/plots/"
        os.makedirs(save_folder, exist_ok=True)
        save_path = f"{save_folder}/{symbol}_{timeframe.value}.jpg"
        addplots = []
        
        addplots = self._add_ema_sma(addplots, df, timeframe) if ema_sma else addplots
        addplots = self._add_rsi(addplots, df) if rsi else addplots
        p = 2 if rsi else 1
        addplots = self._add_macd(addplots, df, p) if macd else addplots
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        
            mpf.plot(
                df, 
                type="candle", 
                style="charles",
                title=symbol, 
                volume=False,
                addplot=addplots,
                figsize=(23, 10),
                savefig=dict(fname=save_path, dpi=300)
            )
        
        logger.info(f"График {symbol}_{timeframe.value} успешно сохранен в {save_path}")
        return save_path
    
    def _load_data(self, timeframe: Timeframe) -> pd.DataFrame:
        data_path = f"data/results/historical_data_{timeframe.value}.parquet"
        return pd.read_parquet(data_path)
    
    def _prepare_data(self, symbol: str, timeframe: Timeframe) -> pd.DataFrame:
        """
        Фильтрует данные по символу и подготавливает их для построения графика.
        """
        df = self._load_data(timeframe)
        df = df[df["symbol"] == symbol].copy()

        if df.empty:
            return None

        df["Date"] = pd.to_datetime(df["Timestamp"], unit="s")
        df.set_index("Date", inplace=True)

        return df
    
    def _add_ema_sma(self, addplots: list, df: pd.DataFrame, timeframe: Timeframe) -> list:
        periods = {
            Timeframe.M15: (9, 21),
            Timeframe.M30: (12, 50),
            Timeframe.H1: (21, 50),
            Timeframe.H4: (21, 100),
            Timeframe.D1: (50, 200),
        }
        ema_period, sma_period = periods.get(timeframe)

        ema = df["Close"].ewm(span=ema_period, adjust=False).mean()
        addplots.append(mpf.make_addplot(ema, width=1, color="orange"))
        
        sma = df["Close"].rolling(sma_period).mean()
        addplots.append(mpf.make_addplot(sma, width=1, color="blue"))
        
        return addplots
    
    def _add_rsi(self, addplots: list, df: pd.DataFrame) -> list:
        # Считаем RSI
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        addplots.append(
            mpf.make_addplot(df["RSI"], panel=1, color="purple", ylabel="RSI")
        )

        addplots.append(
            mpf.make_addplot([70]*len(df), panel=1, color="red", linestyle="dashed")
        )
        addplots.append(
            mpf.make_addplot([30]*len(df), panel=1, color="green", linestyle="dashed")
        )

        return addplots
    
    def _add_macd(self, addplots: list, df: pd.DataFrame, p) -> list:
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()

        df["MACD"] = ema12 - ema26
        df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_hist"] = df["MACD"] - df["MACD_signal"]

        addplots.append(
            mpf.make_addplot(df["MACD"], panel=p, color="blue", ylabel="MACD")
        )
        addplots.append(
            mpf.make_addplot(df["MACD_signal"], panel=p, color="orange")
        )
        addplots.append(
            mpf.make_addplot(df["MACD_hist"], type="bar", panel=p, alpha=0.5)
        )

        return addplots
    

if __name__ == "__main__":
    plotter = MarketPlotter()
    img = plotter.plot_candles(ema_sma=True, rsi=True, macd=True, fvg=True)
 