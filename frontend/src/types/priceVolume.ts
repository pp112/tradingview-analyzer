export interface PriceVolumeEntry {
  price_delta_prc: number;
  volume_delta_prc: number;
}

export type PriceVolumeData = Record<string, PriceVolumeEntry>;