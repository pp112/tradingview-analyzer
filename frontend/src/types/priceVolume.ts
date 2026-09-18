export interface PriceVolumeEntry {
  symbol: string;
  priceDeltaPct: number;
  volumeDeltaPct: number;
}

export type PriceVolumeData = PriceVolumeEntry[];
