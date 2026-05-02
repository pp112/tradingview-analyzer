// ─── Хранилище сигналов ───────────────────────────────────────────────────

const _signals = {
  "1h": [
    { symbol: "ETH/USDT",  indicator: "RSI", indicator_value: 76.06, direction: "ВНИЗ", vol_ratio: 1.5, correlation: 0.91, timeframe: "1h" },
    { symbol: "ZBT/USDT",  indicator: "RSI", indicator_value: 70.52, direction: "ВНИЗ", vol_ratio: 2.2, correlation: 0.7,  timeframe: "1h" },
    { symbol: "LDO/USDT",  indicator: "RSI", indicator_value: 88.39, direction: "ВНИЗ", vol_ratio: 3.5, correlation: 0.65, timeframe: "1h" },
    { symbol: "LDO/USDT",  indicator: "RSI", indicator_value: 88.39, direction: "ВНИЗ", vol_ratio: 4.5, correlation: 0.65, timeframe: "1h" },
  ],
  "4h": [
    { symbol: "KAT/USDT",  indicator: "RSI",     indicator_value: 28.08,              direction: "ВВЕРХ", vol_ratio: 12.13, correlation: -0.83, timeframe: "4h" },
    { symbol: "OPG/USDT",  indicator: "MACD",    indicator_value: 0.0793723991114607, direction: "ВВЕРХ", vol_ratio: 12.13, correlation: 0.77,  timeframe: "4h" },
  ],
  "30m": [
    { symbol: "XAU/USDT",    indicator: "EMA_SMA", indicator_value: 0.08799516178896738,  direction: "ВВЕРХ", vol_ratio: 12.13, correlation: 0.6,  timeframe: "30m" },
    { symbol: "PIPPIN/USDT", indicator: "EMA_SMA", indicator_value: 5.586622931205015e-6, direction: "ВНИЗ",  vol_ratio: 12.13, correlation: -0.72, timeframe: "30m" },
    { symbol: "NAORIS/USDT", indicator: "RSI",     indicator_value: 81.25,               direction: "ВНИЗ",  vol_ratio: 12.13, correlation: 0.73,  timeframe: "30m" },
  ],
};

export function getSignals(timeframe) {
  return _signals[timeframe] || [];
}

export function setSignals(timeframe, data) {
  _signals[timeframe] = data;
}
