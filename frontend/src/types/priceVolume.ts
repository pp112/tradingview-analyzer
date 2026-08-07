export interface PriceVolumeEntry {
  symbol: string;
  price_delta_pct: number;
  volume_delta_pct: number;
}

export type PriceVolumeData = PriceVolumeEntry[];