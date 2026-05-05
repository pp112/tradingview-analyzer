// ─── Обработчики SSE событий ─────────────────────────────────────────────

import { fetchSignals, fetchPriceVolume, fetchInitialData } from "./api.js"
import { renderBottomCards } from "./price_volume.js";
import { setSignals } from "./signals.js";
import { getState } from "./state.js";
import { renderTable } from "./table.js";

// ── Обновление всех данных ───────────────────────────────────────────────

export async function onInit() {
  const { signals, price_changes } = await fetchInitialData();

  for (const [timeframe, data] of Object.entries(signals)) {
    setSignals(timeframe, data);
  }
  renderTable();
  
  if (price_changes) {
    renderBottomCards(price_changes);
  }

  console.log(`Начальное обновление выполнено. Получены: ${Object.keys(signals)}`);
}

// ── Обновление сигналов по таймфрейму ────────────────────────────────────

export async function onSignals(timeframe) {
  const data = await fetchSignals(timeframe);
  if (!data) return;

  setSignals(timeframe, data);

  if (timeframe === getState().timeframe) {
    renderTable();
  }

  console.log(`Сигналы обновлены: ${timeframe}`);
}

// ── Обновление цен и объёмов ─────────────────────────────────────────────

export async function onPriceVolume() {
  const data = await fetchPriceVolume();
  if (!data) return;

  renderBottomCards(data);

  console.log("Изменения цен и объёмов обновлены");
}
