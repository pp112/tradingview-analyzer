import logging
import os
import json
from pandas import DataFrame

from indicators import rsi, macd, moving_average, correlation
from utils import get_symbol_df, sort_correlations, filter_low_correlations

logger = logging.getLogger(__name__)


class IndicatorEngine:

    INDICATORS_DIR = "data/value_indicators"

    def __init__(
        self, 
        upper_threshold_rsi = 70, 
        lower_threshold_rsi = 30, 
        corrs_threshold = 0.5
    ):
        self.upper_threshold_rsi = upper_threshold_rsi
        self.lower_threshold_rsi = lower_threshold_rsi
        self.corrs_threshold = corrs_threshold

    def check_signals(self, df, timeframe):
        signals = []
        result_indicators = self._calculate(df, timeframe)
        
        for symbol, values in result_indicators.items():
            
            rsi_val = values["rsi"]
            macd_prev, macd_curr = values["macd"]
            ema_prev, ema_curr = values["ema"]
            sma_prev, sma_curr = values["sma"]

            if rsi_val > self.upper_threshold_rsi:
                signals.append({
                    "symbol": symbol,
                    "signal": "RSI_OVERBOUGHT",
                    "timeframe": timeframe.value
                })
                logger.info(f"{symbol}: сигнал ВНИЗ, RSI, таймфрейм {timeframe.value}")
            
            elif rsi_val < self.lower_threshold_rsi:
                signals.append({
                    "symbol": symbol,
                    "signal": "RSI_OVERSOLD",
                    "timeframe": timeframe.value
                })
                logger.info(f"{symbol}: сигнал ВВЕРХ, RSI, таймфрейм {timeframe.value}")
            
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
                logger.info(f"{symbol}: сигнал ВВЕРХ, MACD, таймфрейм {timeframe.value}")

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
                logger.info(f"{symbol}: сигнал ВНИЗ, MACD, таймфрейм {timeframe.value}")

            if ema_prev < sma_prev and ema_curr > sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BULLISH",
                    "timeframe": timeframe.value
                })
                logger.info(f"{symbol}: сигнал ВВЕРХ, EMA_SMA, таймфрейм {timeframe.value}")

            elif ema_prev > sma_prev and ema_curr < sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BEARISH",
                    "timeframe": timeframe.value
                })
                logger.info(f"{symbol}: сигнал ВНИЗ, EMA_SMA, таймфрейм {timeframe.value}")
        
        self._save_ind_and_sig(result_indicators, signals, timeframe)

    def update_correlations(self, df: DataFrame):
        ticker_corrs = {}

        symbols = df['symbol'].unique()

        for symbol in symbols:
            ticker_corrs[symbol] = correlation(df, symbol)
        
        ticker_corrs = filter_low_correlations(ticker_corrs, self.corrs_threshold)
        ticker_corrs = sort_correlations(ticker_corrs, "desc")

        self._save_corrs(ticker_corrs)

    def _calculate(self, df, timeframe) -> dict[str, dict]:
        result = {}

        symbols = df['symbol'].unique()

        for symbol in symbols:
            symbol_df = get_symbol_df(symbol, df)

            result[symbol] = {
                "rsi": rsi(symbol_df),
                "macd": macd(symbol_df),
                "ema": moving_average(symbol_df, timeframe, 'ema'),
                "sma": moving_average(symbol_df, timeframe, 'sma')
            }
        
        return result
    
    def _save_ind_and_sig(self, indicators, signals, timeframe):
        self._ensure_dir()

        with open(f"{self.INDICATORS_DIR}/values_{timeframe.value}.json", "w", encoding="utf-8") as f:
            json.dump(indicators, f, indent=4, ensure_ascii=False)

        with open(f"{self.INDICATORS_DIR}/signals_{timeframe.value}.json", "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=4, ensure_ascii=False)

        logger.info(f"Результаты индикаторов и сигналов успешно сохранены в {self.INDICATORS_DIR}")
        
    def _save_corrs(self, ticker_corrs):
        self._ensure_dir()

        with open(f"{self.INDICATORS_DIR}/correlations.json", "w", encoding="utf-8") as f:
            json.dump(ticker_corrs, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Результаты корреляции успешно сохранены в {self.INDICATORS_DIR}")

    def _ensure_dir(self):
        os.makedirs(self.INDICATORS_DIR, exist_ok=True)