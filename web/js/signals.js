// ─── Хранилище сигналов ───────────────────────────────────────────────────

// const signals = {
//   "1h": [
//     { symbol: "ETH/USDT",  indicator: "rsi", indicator_value: 76.06, direction: "ВНИЗ", vol_ratio: 1.2, correlation: 0.11, timeframe: "1h" },
//     { symbol: "ETH/USDT",  indicator: "macd", indicator_value: 0.05, direction: "ВНИЗ", vol_ratio: 1.3, correlation: 0.21, timeframe: "1h" },
//     { symbol: "ETH/USDT",  indicator: "ema_sma", indicator_value: 0.32, direction: "ВНИЗ", vol_ratio: 1.4, correlation: 0.31, timeframe: "1h" },
//     { symbol: "ZBT/USDT",  indicator: "rsi", indicator_value: 70.52, direction: "ВНИЗ", vol_ratio: 2.2, correlation: 0.47,  timeframe: "1h" },
//     { symbol: "ZBT/USDT",  indicator: "macd", indicator_value: 7.52, direction: "ВНИЗ", vol_ratio: 2.4, correlation: 0.57,  timeframe: "1h" },
//     { symbol: "LDO/USDT",  indicator: "rsi", indicator_value: 88.9, direction: "ВНИЗ", vol_ratio: 3.5, correlation: 0.65, timeframe: "1h" },
//     { symbol: "BTC/USDT",  indicator: "rsi", indicator_value: 88.19, direction: "ВВЕРХ", vol_ratio: 4.4, correlation: 0.75, timeframe: "1h" },
//     { symbol: "ZXC/USDT",  indicator: "rsi", indicator_value: 88.29, direction: "ВВЕРХ", vol_ratio: 4.5, correlation: 0.85, timeframe: "1h" },
//   ],
//   "4h": [
//     { symbol: "KAT/USDT",  indicator: "rsi",     indicator_value: 28.08,              direction: "ВВЕРХ", vol_ratio: 12.13, correlation: -0.83, timeframe: "4h" },
//     { symbol: "OPG/USDT",  indicator: "macd",    indicator_value: 0.0793723991114607, direction: "ВВЕРХ", vol_ratio: 12.13, correlation: 0.77,  timeframe: "4h" },
//   ],
//   "30m": [
//     { symbol: "XAU/USDT",    indicator: "ema_sma", indicator_value: 0.08799516178896738,  direction: "ВВЕРХ", vol_ratio: 12.13, correlation: 0.6,  timeframe: "30m" },
//     { symbol: "PIPPIN/USDT", indicator: "ema_sma", indicator_value: 5.586622931205015e-6, direction: "ВНИЗ",  vol_ratio: 12.13, correlation: -0.72, timeframe: "30m" },
//     { symbol: "NAORIS/USDT", indicator: "rsi",     indicator_value: 81.25,               direction: "ВНИЗ",  vol_ratio: 12.13, correlation: 0.73,  timeframe: "30m" },
//   ],
// };

const signals = {};

export function getSignals(timeframe) {
  return signals[timeframe] || [];
}

export function setSignals(timeframe, data) {
  signals[timeframe] = data.map(formatSignal);
}

function formatSignal(signal) {
  return {
    ...signal,
    symbol:          signal.symbol.replace(".P", "").replace("USDT", "/USDT"),
    indicator_value: Number(signal.indicator_value.toFixed(2)),
    vol_ratio:       Number(signal.vol_ratio.toFixed(2)),
  };
}