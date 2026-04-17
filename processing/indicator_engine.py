import logging
import os
import json

from pandas import DataFrame

from processing import rsi, macd, moving_average, correlation
from utils import get_symbol_df, sort_correlations, filter_low_correlations
from models.timeframe import Timeframe

logger = logging.getLogger(__name__)


class IndicatorEngine:
    """
    Расчёт индикаторов, сигналов и корреляций.

    Формирует:
    - RSI / MACD / MA сигналы
    - торговые алерты
    - корреляции между активами
    - отчёты и файлы результатов
    """
    INDICATORS_DIR = "data/value/indicators"
    SIGNALS_DIR = "data/value/signals"
    CORRELATIONS_DIR = "data/value/correlations"
    REPORTS_DIR = "data/reports"

    def __init__(
        self, 
        upper_threshold_rsi = 70, 
        lower_threshold_rsi = 30, 
        corr_threshold = 0.5
    ):
        self.upper_threshold_rsi = upper_threshold_rsi
        self.lower_threshold_rsi = lower_threshold_rsi
        self.corr_threshold = corr_threshold

    def process(
        self, 
        df: DataFrame, 
        timeframe: Timeframe
    ) -> tuple[
        dict[str, dict], 
        list[dict], 
        list[str]
    ]:
        """
        Проверяет торговые сигналы по всем символам:
        RSI, MACD, EMA/SMA пересечения.
        """
        indicators: dict[str, dict] = {}
        signals: list[dict] = []
        reports: list[str] = []

        symbols = df["symbol"].unique()
        
        for symbol in symbols:
            symbol_df = df[df["symbol"] == symbol]
            
            rsi_val = rsi(symbol_df)
            macd_prev, macd_curr = macd(symbol_df)
            ema_prev, ema_curr = moving_average(symbol_df, timeframe, "ema")
            sma_prev, sma_curr = moving_average(symbol_df, timeframe, "sma")

            indicators[symbol] = {
                "rsi": rsi_val,
                "macd": {
                    "prev": macd_prev,
                    "curr": macd_curr
                },
                "ema": (ema_prev, ema_curr),
                "sma": (sma_prev, sma_curr)
            }

            # ===== RSI =====
            if rsi_val > self.upper_threshold_rsi:
                signals.append({
                    "symbol": symbol,
                    "signal": "RSI_OVERBOUGHT",
                    "timeframe": timeframe.value
                })
                reports.append(self._formated_line(symbol, "RSI", "ВНИЗ", timeframe))
            
            elif rsi_val < self.lower_threshold_rsi:
                signals.append({
                    "symbol": symbol,
                    "signal": "RSI_OVERSOLD",
                    "timeframe": timeframe.value
                })
                reports.append(self._formated_line(symbol, "RSI", "ВВЕРХ", timeframe))
            
            if (
                macd_prev["MACD"] < macd_prev["MACD_signal"]
                and macd_curr["MACD"] > macd_curr["MACD_signal"]
                and macd_curr["MACD"] < 0
            ):
                signals.append({
                    "symbol": symbol,
                    "signal": "MACD_BULLISH",
                    "timeframe": timeframe.value
                })
                reports.append(self._formated_line(symbol, "MACD", "ВВЕРХ", timeframe))

            elif (
                macd_prev["MACD"] > macd_prev["MACD_signal"]
                and macd_curr["MACD"] < macd_curr["MACD_signal"]
                and macd_curr["MACD"] > 0
            ):
                signals.append({
                    "symbol": symbol,
                    "signal": "MACD_BEARISH",
                    "timeframe": timeframe.value
                })
                reports.append(self._formated_line(symbol, "MACD", "ВНИЗ", timeframe))

            if ema_prev < sma_prev and ema_curr > sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BULLISH",
                    "timeframe": timeframe.value
                })
                reports.append(self._formated_line(symbol, "EMA_SMA", "ВВЕРХ", timeframe))

            elif ema_prev > sma_prev and ema_curr < sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BEARISH",
                    "timeframe": timeframe.value
                })
                reports.append(self._formated_line(symbol, "EMA_SMA", "ВНИЗ", timeframe))
        
        return indicators, signals, reports

    def calculate_correlations(self, df: DataFrame) -> dict[str, float]:
        """
        Рассчитывает корреляции всех символов относительно BTC.
        """
        ticker_corrs: dict[str, float] = {}

        symbols = df['symbol'].unique()

        for symbol in symbols:
            ticker_corrs[symbol] = correlation(df, symbol)
        
        ticker_corrs = filter_low_correlations(ticker_corrs, self.corr_threshold)
        ticker_corrs = sort_correlations(ticker_corrs, "desc")

        return ticker_corrs
    
    def _save_ind_and_sig(self, indicators, signals, timeframe: Timeframe):
        self._ensure_dir(self.INDICATORS_DIR)
        self._ensure_dir(self.SIGNALS_DIR)

        file_path_i = f"{self.INDICATORS_DIR}/values_{timeframe.label}.json"
        file_path_s = f"{self.SIGNALS_DIR}/signals_{timeframe.label}.json"

        with open(file_path_i, "w", encoding="utf-8") as f:
            json.dump(indicators, f, indent=4, ensure_ascii=False)

        with open(file_path_s, "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=4, ensure_ascii=False)

        logger.info(f"Значения индикаторов {timeframe.label} успешно сохранены: {file_path_i}")
        logger.info(f"Значения сигналов {timeframe.label} успешно сохранены: {file_path_s}")

    def _save_corrs(self, ticker_corrs):
        self._ensure_dir(self.CORRELATIONS_DIR)

        file_path = f"{self.CORRELATIONS_DIR}/correlations.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ticker_corrs, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Значения корреляций успешно сохранены: {file_path}")

    def _save_reports(self, reports, timeframe: Timeframe):
        self._ensure_dir(self.REPORTS_DIR)

        file_path = f"{self.REPORTS_DIR}/signals_{timeframe.label}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            for line in reports:
                f.write(line)

        logger.info(f"Сигналы таймфрейма {timeframe.label} успешно сохранены в {file_path}")

    def _ensure_dir(self, path: str):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def _formated_line(symbol, indicator, signal, timeframe):
        return f"| {symbol:<14} | {signal:<5} | {indicator:<7} | {timeframe.label:<3}"