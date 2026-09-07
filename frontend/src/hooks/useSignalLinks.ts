import { useEffect } from "react";
import { fetchLinkedSinglaValues, fetchOrderLinks, fetchPositionLinks } from "../api/signalLinks";
import { useSignalLinksStore } from "../store/useSignalLinksStore";
import type { Timeframe } from "../types/signal";

export function useSignalLinks() {
  const setPositionLinks = useSignalLinksStore((s) => s.setPositionLinks);
  const setOrderLinks = useSignalLinksStore((s) => s.setOrderLinks);
  const setCurrentValues = useSignalLinksStore((s) => s.setCurrentValues);

  useEffect(() => {
    Promise.all([fetchPositionLinks(), fetchOrderLinks()])
      .then(async ([positionLinks, orderLinks]) => {
        setPositionLinks(positionLinks);
        setOrderLinks(orderLinks);

        const timeframes = new Set<Timeframe>([
          ...positionLinks.map((l) => l.signal.timeframe),
          ...orderLinks.map((l) => l.signal.timeframe),
        ]);

        await Promise.all(
          Array.from(timeframes).map(async (tf) => {
            try {
              const values = await fetchLinkedSinglaValues(tf);
              if (values.length > 0) {
                setCurrentValues(values, tf);
              }
            } catch (err) {
              console.error(`Ошибка загрузки текущих значений для ${tf}:`, err);
            }
          })
        );
      })
      .catch((err) => {
        console.error("Не удалось загрузить привязки сигналов:", err);
      });
  }, [setPositionLinks, setOrderLinks, setCurrentValues]);
}
