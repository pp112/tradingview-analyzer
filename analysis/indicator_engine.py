import logging
import json

from indicators import rsi, macd, moving_average
from utils import load_data, get_symbol_df

logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] - %(message)s",
    )


class IndicatorEngine:
    def __init__(self, upper_threshold_rsi = 70, lower_threshold_rsi = 30):
        self.upper_threshold_rsi = upper_threshold_rsi
        self.lower_threshold_rsi = lower_threshold_rsi

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
                logger.info(f"RSI: сигнал ВНИЗ для {symbol} на таймфрейме {timeframe.value}")
            
            elif rsi_val < self.lower_threshold_rsi:
                signals.append({
                    "symbol": symbol,
                    "signal": "RSI_OVERSOLD",
                    "timeframe": timeframe.value
                })
                logger.info(f"RSI: сигнал ВВЕРХ для {symbol} на таймфрейме {timeframe.value}")
            
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
                logger.info(f"MACD: сигнал ВВЕРХ для {symbol} на таймфрейме {timeframe.value}")

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
                logger.info(f"MACD: сигнал ВНИЗ для {symbol} на таймфрейме {timeframe.value}")

            if ema_prev < sma_prev and ema_curr > sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BULLISH",
                    "timeframe": timeframe.value
                })
                logger.info(f"EMA_SMA: сигнал ВВЕРХ для {symbol} на таймфрейме {timeframe.value}")

            elif ema_prev > sma_prev and ema_curr < sma_curr:
                signals.append({
                    "symbol": symbol,
                    "signal": "EMA_SMA_BEARISH",
                    "timeframe": timeframe.value
                })
                logger.info(f"EMA_SMA: сигнал ВНИЗ для {symbol} на таймфрейме {timeframe.value}")
        
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
    
    def _save_to_files(self, indicators, signals, timeframe):
        save_dir = "data/indicators"

        with open(f"{save_dir}/indicators_{timeframe.value}.json", "w", encoding="utf-8") as f:
            json.dump(indicators, f, indent=4, ensure_ascii=False)

        with open(f"{save_dir}/signals_{timeframe.value}.json", "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=4, ensure_ascii=False)

        logger.info("Результаты indicators и signals успешно сохранены ")
        
