import logging
import warnings
from pathlib import Path

import pandas as pd
import mplfinance as mpf

from models import Timeframe
from utils import load_data, filter_by_symbol
from processing.indicator_service import IndicatorService

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
        symbol: str,
        save_folder: str,
        filename: str,
        timeframe: Timeframe,
        ema_sma: bool = True,
        rsi: bool = True,
        macd: bool = True
    ) -> str:
        """
        Строит свечной график криптовалютного инструмента с возможностью добавления
        технических индикаторов и сохраняет его в файл.
        """
        df = self._prepare_data(symbol, timeframe)
        if df is None:
            logger.error(f"Нет данных для {symbol}")
            return
        
        save_folder = Path(save_folder)
        save_folder.mkdir(parents=True, exist_ok=True)
        save_path = save_folder / f"{filename}.jpg"

        addplots = []
        
        if ema_sma:
            addplots = self._add_ema_sma(addplots, df, timeframe)

        if rsi:
            addplots = self._add_rsi(addplots, df)

        if macd:
            addplots = self._add_macd(addplots, df, panel=2 if rsi else 1)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        
            mpf.plot(
                df, 
                type="candle", 
                style="charles",
                title=symbol, 
                volume=False,
                addplot=addplots,
                figsize=(16, 9),
                savefig=dict(fname=save_path, dpi=400)
            )
        
        return save_path
    
    def _prepare_data(self, symbol: str, timeframe: Timeframe) -> pd.DataFrame:
        """
        Загружает исторические данные и фильтрует их по символу.
        Преобразует timestamp в datetime индекс для mplfinance.
        """
        df = load_data(timeframe)
        df = filter_by_symbol(symbol, df)

        if df.empty:
            return None

        df["Date"] = pd.to_datetime(df["timestamp"], unit="s")
        df.set_index("Date", inplace=True)

        return df
    
    def _add_ema_sma(self, addplots: list, df: pd.DataFrame, timeframe: Timeframe) -> list:
        """
        Добавляет на график EMA и SMA линии для заданного таймфрейма.
        """
        ema_series = IndicatorService.ema_series(df, timeframe)
        sma_series = IndicatorService.sma_series(df, timeframe)
        
        addplots.append(mpf.make_addplot(ema_series, width=1, color="orange"))
        addplots.append(mpf.make_addplot(sma_series, width=1, color="blue"))
        
        return addplots
    
    def _add_rsi(self, addplots: list, df: pd.DataFrame) -> list:
        """
        Рассчитывает RSI и добавляет его на отдельную панель графика.
        Также добавляет уровни перекупленности и перепроданности.
        """
        rsi = IndicatorService.rsi_series(df)

        if rsi is None:
            return addplots

        addplots.append(mpf.make_addplot(rsi, panel=1, color="purple", ylabel="RSI"))
        addplots.append(mpf.make_addplot([70] * len(df), panel=1, color="red", linestyle="dashed"))
        addplots.append(mpf.make_addplot([30] * len(df), panel=1, color="green", linestyle="dashed"))

        return addplots
    
    def _add_macd(self, addplots: list, df: pd.DataFrame, panel) -> list:
        """
        Рассчитывает MACD, сигнальную линию и гистограмму.
        Добавляет их на отдельную панель графика.
        """
        macd_df = IndicatorService.macd_series(df)

        if macd_df is None:
            return addplots

        addplots.append(mpf.make_addplot(macd_df["MACD"], panel=panel, color="blue", ylabel="MACD"))
        addplots.append(mpf.make_addplot(macd_df["MACD_signal"], panel=panel, color="orange"))
        addplots.append(mpf.make_addplot(macd_df["HIST"], type="bar", panel=panel, alpha=0.5))

        return addplots


if __name__ == "__main__":
    plotter = MarketPlotter()
    img = plotter.plot_candles(
        symbol="BTCUSDT.P",
        timeframe=Timeframe.H1,
        save_folder="visualization",
        filename="1",
        ema_sma=True, 
        rsi=True, 
        macd=True)