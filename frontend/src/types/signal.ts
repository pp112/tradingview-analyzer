import type { PriceVolumeData } from "./priceVolume";

export type Timeframe = "15m" | "30m" | "1h" | "4h" | "1d";

export type IndicatorType = "rsi" | "macd" | "ema_sma" | "vol_ratio";

export type Direction = "ВВЕРХ" | "ВНИЗ";

export type Sigtype = "all" | "strong" | "combined";

export type Signal = {
  symbol: string;
  indicator: Exclude<IndicatorType, "vol_ratio">;
  indicator_value: number;
  direction: Direction;
  vol_ratio: number;
  correlation: number;
  timeframe: Timeframe;
}

export type CombinedSignal = {
  symbol: string;
  direction: Direction;
  rsi: number | null;
  macd: number | null;
  ema_sma: number | null;
  vol_ratio: number;
  correlation: number;
}

export type SortColumn =
  | "symbol"
  | "indicator_value"
  | "indicator"
  | "direction"
  | "vol_ratio"
  | "correlation"
  | "rsi"
  | "macd"
  | "ema_sma";

export type SortState = {
  column: SortColumn | null;
  direction: 0 | 1 | 2; // 0 = нет сортировки, 1 = убывание, 2 = возрастание
}

export type SSEMessage =
  | { type: "signals"; timeframe: Timeframe }
  | { type: "price_volume" };

export type InitialDataResponse = {
  signals: Partial<Record<Timeframe, Signal[]>>;
  price_changes: PriceVolumeData | null;
}
