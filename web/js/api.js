// ─── API: получение данных и SSE ──────────────────────────────────────────
// Знает про сервер. Форматирует данные. Записывает в store. Не трогает UI.

import { setSignals, getSignals } from "./signals.js";
import { getState } from "./state.js";
import { renderTable } from "./table.js";

const API = "http://localhost:8000";

// ── SSE подписка на обновления ─────────────────────────────────────────────

export function connectSSE() {
  const eventSource = new EventSource(`${API}/stream`);

  eventSource.addEventListener("update", (event) => {
    const data = JSON.parse(event.data);
    console.log(`Пришло сообщение обновления: ${data.type}`);
    
    if (data.type === "signals") {
      fetchSignals(data.timeframe);
    } else if (data.type === "price_volume"){
      fetchPriceVolume();
    }
  });

  eventSource.onerror = (err) => {
    console.error("SSE ошибка:", err);
  };
}

// ── Запрос сигналов по таймфрейму ──────────────────────────────────────────

async function fetchSignals(tf) {
  try {
    const res  = await fetch(`${API}/signals?tf=${tf}`);
    const data = await res.json();

    setSignals(tf, data.map(formatSignal));
    console.log(`Данные обновлены: ${tf}`);

    if (tf === getState().timeframe) {
      renderTable();
    }
  } catch (err) {
    console.error(`Ошибка загрузки сигналов (${tf}):`, err);
  }
}

// ── Запрос изменений цен и объемов ─────────────────────────────────────────

async function fetchPriceVolume() {
    const res  = await fetch(`${API}/price_volume`);
    const data = await res.json();
    console.log("Изменения цен и объемов обновлены");
}

// ── Форматирование сырых данных ────────────────────────────────────────────

function formatSignal(signal) {
  return {
    ...signal,
    symbol:          signal.symbol.replace(".P", "").replace("USDT", "/USDT"),
    indicator_value: Number(signal.indicator_value.toFixed(2)),
    vol_ratio:       Number(signal.vol_ratio.toFixed(2)),
  };
}
