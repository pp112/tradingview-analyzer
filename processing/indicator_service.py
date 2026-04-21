import pandas as pd

from models.timeframe import Timeframe
from utils import filter_by_symbol
from config import get_logger

logger = get_logger(__name__)


class IndicatorService:
    """
    Сервис расчёта технических индикаторов.
    """
    @staticmethod
    def rsi_series(symbol_df: pd.DataFrame) -> pd.Series | None:
        """
        Полная RSI серия (для графиков и анализа)
        """
        try:
            length = 14
            delta = symbol_df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.ewm(alpha=1/length, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/length, adjust=False).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        except Exception:
            logger.warning(f"RSI: ошибка расчёта серии")
            return None

    @staticmethod
    def rsi_last(symbol_df: pd.DataFrame) -> float | None:
        """
        Последнее значение RSI (для сигналов)
        """
        try:
            rsi = IndicatorService.rsi_series(symbol_df)
            rsi = rsi.dropna()

            if rsi.empty:
                return None
            
            return round(float(rsi.iloc[-1]), 2)
        
        except Exception:
            logger.warning(f"RSI: ошибка получения последних значений")
            return None

    @staticmethod
    def rsi_extremes(
        symbol_df: pd.DataFrame, 
        top_n: int
    ) -> dict[str, list[float]] | None:
        try:
            s = IndicatorService.rsi_series(symbol_df).dropna()

            if len(s) < top_n:
                return None

            top = s.nlargest(top_n).values
            bottom = s.nsmallest(top_n).values

            return {
                "top": [round(x, 2) for x in top.tolist()],
                "bottom": [round(x, 2) for x in bottom.tolist()]
            }
        except Exception:
            logger.warning(f"RSI: ошибка расчета экстремумов")
            return None
    
    @staticmethod
    def macd_series(symbol_df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Полный MACD DataFrame:
        - MACD
        - signal
        - histogram
        """
        try:
            ema_fast = symbol_df["Close"].ewm(span=12, adjust=False).mean()
            ema_slow = symbol_df["Close"].ewm(span=26, adjust=False).mean()

            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            
            return pd.DataFrame({
                "MACD": macd_line,
                "MACD_signal": signal_line,
                "HIST": macd_line - signal_line
            })
        
        except Exception:
            logger.warning(f"MACD: ошибка расчёта серии")
            return None

    @staticmethod
    def macd_last(
        symbol_df: pd.DataFrame
    ) -> dict[str, dict[str, float]] | None:
        """
        Последние 2 значения MACD (prev, curr)
        """
        try:
            macd_df = IndicatorService.macd_series(symbol_df).dropna()

            if len(macd_df) < 2:
                return None

            prev_df, curr_df = macd_df.iloc[-2], macd_df.iloc[-1]
            prev = {
                "MACD": float(prev_df["MACD"]),
                "MACD_signal": float(prev_df["MACD_signal"])
            }
            curr = {
                "MACD": float(curr_df["MACD"]),
                "MACD_signal": float(curr_df["MACD_signal"])
            }
            return {
                "prev": prev,
                "curr": curr
            }
        
        except Exception:
            logger.warning(f"MACD: ошибка получения последних значений")
            return None

    @staticmethod
    def ema_series(symbol_df: pd.DataFrame, timeframe: Timeframe) -> pd.Series:
        """
        Полная EMA серия
        """
        period, _ = IndicatorService.ema_sma_periods(timeframe)
        return symbol_df["Close"].ewm(span=period, adjust=False).mean()

    @staticmethod
    def sma_series(symbol_df: pd.DataFrame, timeframe: Timeframe) -> pd.Series:
        """
        Полная SMA серия
        """
        _, period = IndicatorService.ema_sma_periods(timeframe)
        return symbol_df["Close"].rolling(period).mean()

    @staticmethod
    def ema_last(
        symbol_df: pd.DataFrame, 
        timeframe: Timeframe
    ) -> tuple[float, float] | None:
        """
        Последние 2 значения EMA (prev, curr)
        """
        ema = IndicatorService.ema_series(symbol_df, timeframe).dropna()
        if len(ema) < 2:
            return None
        return float(ema.iloc[-2]), float(ema.iloc[-1])

    @staticmethod
    def sma_last(symbol_df: pd.DataFrame, timeframe: Timeframe) -> float | None:
        """
        Последние 2 значения SMA (prev, curr)
        """
        sma = IndicatorService.sma_series(symbol_df, timeframe).dropna()
        if len(sma) < 2:
            return None
        return float(sma.iloc[-2]), float(sma.iloc[-1])

    @staticmethod
    def volume_metrics(
        symbol_df: pd.DataFrame, 
        timeframe: Timeframe
    ) -> dict[str, float] | None:
        """
        Рассчитывает метрики объёма.
        """
        try:
            window = IndicatorService.volume_window_for(timeframe)

            if len(symbol_df) < window:
                return None

            avg_volume = symbol_df["Volume"].rolling(window).mean().iloc[-1]
            curr_volume = symbol_df["Volume"].iloc[-1]

            if pd.isna(avg_volume) or avg_volume == 0:
                return None

            return {
                "curr": float(curr_volume),
                "avg": float(avg_volume),
                "ratio": float(curr_volume / avg_volume)
            }
        except Exception:
            logger.warning(f"VOLUME: ошибка расчета метрик объема")
            return None

    @staticmethod
    def correlation(symbol_df: pd.DataFrame, symbol: str) -> float | None:
        """
        Корреляция с BTC
        """
        try:
            df_btc = filter_by_symbol("BTCUSDT.P", symbol_df)
            df_alt = filter_by_symbol(symbol, symbol_df)

            df_btc["Date"] = pd.to_datetime(df_btc["Timestamp"], unit="s")
            df_alt["Date"] = pd.to_datetime(df_alt["Timestamp"], unit="s")

            df_btc.set_index("Date", inplace=True)
            df_alt.set_index("Date", inplace=True)

            merged = pd.DataFrame({
                "btc": df_btc["Close"],
                "alt": df_alt["Close"]
            }).dropna()

            if len(merged) < 30:
                return None

            corr = merged["alt"].rolling(30).corr(merged["btc"]).iloc[-1]
            if pd.isna(corr):
                return None

            return round(float(corr), 2)

        except Exception:
            logger.warning(f"CORRELATION: ошибка расчета корреляции")
            return None
    
    @staticmethod
    def ema_sma_periods(timeframe: Timeframe) -> tuple[int, int]:
        return {
            Timeframe.M15: (9, 21),
            Timeframe.M30: (12, 50),
            Timeframe.H1: (21, 50),
            Timeframe.H4: (21, 100),
            Timeframe.D1: (50, 200)
        }[timeframe]

    @staticmethod
    def volume_window_for(timeframe: Timeframe) -> int:
        return {
            Timeframe.M15: 10,
            Timeframe.M30: 15,
            Timeframe.H1: 20,
            Timeframe.H4: 30,
            Timeframe.D1: 50,
        }[timeframe]