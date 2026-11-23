import { useEffect } from "react";
import { connectSSE } from "../api/sse";
import { fetchSignals } from "../api/signals";
import { useSignalsStore } from "../store/useSignalsStore";
import { fetchPriceVolume } from "../api/priceVolume";
import type { Timeframe } from "../types/signal";
import { fetchLinkedSignalValues, fetchSignalLinks } from "../api/signalLinks";
import { useSignalLinksStore } from "../store/useSignalLinksStore";
import { fetchPortfolio } from "../api/portfolio";
import { usePortfolioStore } from "../store/usePortfolioStore";

export function useSSE() {
  useEffect(() => {
    const eventSource = connectSSE({
      onSignals: async (timeframe: Timeframe) => {
        try {
          const data = await fetchSignals(timeframe);
          useSignalsStore.getState().setSignals(timeframe, data);
        } catch (err) {
          console.error("Ошибка получения сигналов через SSE:", err);
        }
        try {
          const linkedValues = await fetchLinkedSignalValues(timeframe);
          if (linkedValues.length > 0) {
            useSignalLinksStore
              .getState()
              .setCurrentValues(linkedValues, timeframe);
          }
        } catch (err) {
          console.error("Ошибка получения текущих значений индикаторов:", err);
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
      onPortfolio: async () => {
        try {
          const [portfolio, signalLinks] = await Promise.all([
            fetchPortfolio(),
            fetchSignalLinks(),
          ]);

          usePortfolioStore.getState().setPortfolio(portfolio);

          const linksStore = useSignalLinksStore.getState();
          linksStore.setPositionLinks(signalLinks.positions);
          linksStore.setOrderLinks(signalLinks.orders);
        } catch (err) {
          console.error("Не удалось загрузить позиции/ордера:", err);
        }
      },
    });

    return () => eventSource.close();
  }, []);
}
