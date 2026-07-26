import { apiGet } from "./client";
import type { Timeframe, Signal, InitialDataResponse } from "../types/signal";

export async function fetchSignals(timeframe: Timeframe): Promise<Signal[]> {
  return apiGet<Signal[]>(`/signals?tf=${timeframe}`);
}

export async function fetchInitialData(): Promise<InitialDataResponse> {
  return apiGet<InitialDataResponse>("/initial_data");
}
