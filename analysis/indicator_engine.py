import logging

from indicators import rsi, macd, moving_average
from utils import load_data, get_symbol_df

logger = logging.getLogger(__name__)


class IndicatorEngine:
    def __init__(self):
        self.upper_threshold_rsi = 70
        self.lower_threshold_rsi = 30

    def check_signals(self, timeframe):
        signals = []
        result_indicators = self._calculate(timeframe)
        
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
            elif rsi_val < self.lower_threshold_rsi:
                signals.append({
                    "symbol": symbol,
                    "signal": "RSI_OVERSOLD",
                    "timeframe": timeframe.value
                })

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
            
            if ema_prev < sma_prev and ema_curr > sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BULLISH",
                    "timeframe": timeframe.value
                })
            elif ema_prev > sma_prev and ema_curr < sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BEARISH",
                    "timeframe": timeframe.value
                })
        
        self._save_to_files(result_indicators, signals)

    def _calculate(self, timeframe) -> dict[str, dict]:
        result = {}

        df = load_data(timeframe)
        symbols = df['symbol']

        for symbol in symbols:
            symbol_df = get_symbol_df(symbol)

            result[symbol] = {
                "rsi": rsi(symbol_df),
                "macd": macd(symbol_df),
                "ema": moving_average(symbol_df, timeframe, 'ema'),
                "sma": moving_average(symbol_df, timeframe, 'sma')
            }
        
        return result
    
    def _save_to_files(self, indicators, signals):
        ...