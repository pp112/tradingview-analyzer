import { API_BASE_URL } from "./client";
import type { SSEMessage, Timeframe } from "../types/signal";

interface SSEHandlers {
  onSignals: (timeframe: Timeframe) => void;
  onPriceVolume: () => void;
}

export function connectSSE(handlers: SSEHandlers): EventSource {
  const eventSource = new EventSource(`${API_BASE_URL}`);

  eventSource.addEventListener("update", (event: MessageEvent) => {
    const data: SSEMessage = JSON.parse(event.data);

    if (data.type === "signals") {
      handlers.onSignals(data.timeframe);
    } else if (data.type === "price_volume") {
      handlers.onPriceVolume();
    }
  });

  eventSource.onerror = (err) => {
    console.error("SSE ошибка:", err);
  };

  return eventSource;
}
