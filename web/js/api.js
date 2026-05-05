// ─── API: получение данных и SSE ──────────────────────────────────────────
// Знает про сервер. Форматирует данные. Записывает в store. Не трогает UI.

import { setSignals, getSignals } from "./signals.js";
import { getState } from "./state.js";
import { renderTable } from "./table.js";

const API = "http://localhost:8000";

// ── SSE подписка на обновления ─────────────────────────────────────────────

export function connectSSE(handlers) {
  const eventSource = new EventSource(`${API}/stream`);

  eventSource.addEventListener("update", (event) => {
    const data = JSON.parse(event.data);
    console.log(`Пришло сообщение обновления: ${data.type}`);
    
    if (data.type === "signals") {
      handlers.onSignals(data.timeframe);
    } else if (data.type === "price_volume"){
      handlers.onPriceVolume();
    }
  });

  eventSource.onerror = (err) => {
    console.error("SSE ошибка:", err);
  };
}

// ── Запрос сигналов по таймфрейму ──────────────────────────────────────────

export async function fetchSignals(tf) {
  try {
    const res  = await fetch(`${API}/signals?tf=${tf}`);
    return await res.json();
  } catch (err) {
    console.error(`Ошибка загрузки сигналов (${tf}):`, err);
  }
}

// ── Запрос изменений цен и объемов ─────────────────────────────────────────

export async function fetchPriceVolume() {
  try {
    const res  = await fetch(`${API}/price_volume`);
    return await res.json();
  } catch {
    console.error("Ошибка загрузки цен и объёмов:", err)
  }
}

// ── Запрос начальных актуальных данных ───────────────────────────────────

export async function fetchInitialData() {
  try {
    const res = await fetch(`${API}/initial_data`);
    return await res.json(); // { signals: { "1h": [...] }, price_changes: { ... } | null }
  } catch (err) {
    console.error("Ошибка загрузки начальных данных:", err);
    return { signals: {}, price_changes: null };
  }
}
