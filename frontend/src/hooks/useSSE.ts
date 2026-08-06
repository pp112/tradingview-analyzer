import { useEffect } from "react";
import { connectSSE } from "../api/sse";
import { fetchSignals } from "../api/signals";
import { useSignalsStore } from "../store/useSignalsStore";
import { fetchPriceVolume } from "../api/priceVolume";

export function useSSE() {
  useEffect(() => {
    const eventSource = connectSSE({
      onSignals: async (timeframe) => {
        try {
          const data = await fetchSignals(timeframe);
          useSignalsStore.getState().setSignals(timeframe, data);
        } catch (err) {
          console.error("Ошибка получения сигналов через SSE:", err);
        }
      },
      onPriceVolume: async () => {
        try {
          const data = await fetchPriceVolume();
          useSignalsStore.getState().setPriceVolume(data);
        } catch (err) {
          console.error("Ошибка получения price/volume через SSE:", err);
        }
      },
    });

    return () => eventSource.close();
  }, []);
}