import { apiGet } from "./client";
import type { PriceVolumeData } from "../types/priceVolume";

export async function fetchPriceVolume(): Promise<PriceVolumeData> {
  return apiGet<PriceVolumeData>("/price_volume");
}
