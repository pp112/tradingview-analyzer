// ─── Обработчик кликов по заголовкам таблицы ───────────────────────────────────────────

import { setSortState } from "../state.js";
import { renderTable } from "../table.js";

export function initSort() {
  const table = document.getElementById("signalTable");

  table.addEventListener("click", (e) => {
  const th = e.target.closest("th[data-col]");
  if (!th) return;

  setSortState(th.dataset.col);
  renderTable();
  });
}