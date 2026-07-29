import { useEffect } from "react";
import { connectSSE } from "../api/sse";
import { fetchSignals } from "../api/signals";
import { useSignalsStore } from "../store/useSignalsStore";
import { fetchPriceVolume } from "../api/priceVolume";

export function useSSE() {
  useEffect(() => {
    const eventSource = connectSSE({
      onSignals: async (timeframe) => {
        const data = await fetchSignals(timeframe);
        useSignalsStore.getState().setSignals(timeframe, data);
      },
      onPriceVolume: async () => {
        const data = await fetchPriceVolume();
        useSignalsStore.getState().setPriceVolume(data);
      },
    });

    return () => eventSource.close();
  }, []);
}