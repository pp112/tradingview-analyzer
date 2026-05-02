// ─── Сортировка таблицы ───────────────────────────────────────────────────

import { getState, setSortState } from "./state.js";
import { renderTable } from "./table.js";

// ── Привязка кликов по заголовкам ──────────────────────────────────────────

export function bindSorting() {
  const table = document.getElementById("signalTable");

  table.addEventListener("click", (e) => {
    const th = e.target.closest("th[data-col]");
    if (!th) return;

    setSortState(th.dataset.col);
    renderTable();
  });
}

// ── Применение сортировки к массиву строк ──────────────────────────────────

export function applySorting(rows) {
  const { column, direction } = getState().sort;

  if (!column || direction === 0) return rows;

  const order = direction === 1 ? -1 : 1;

  const sortedRows = [...rows];

  sortedRows.sort((a, b) => {
    const v1 = a[column];
    const v2 = b[column];

    if (typeof v1 === "string") {
      return v1.localeCompare(v2) * order;
    }

    return (v1 - v2) * order;
  });

  return sortedRows;
}

// ── Обновление CSS-классов заголовков ──────────────────────────────────────

export function updateSortCell() {
  const table = document.getElementById("signalTable");
  const ths   = table.querySelectorAll("th[data-col]");

  ths.forEach(th => th.classList.remove("sorted-asc", "sorted-desc"));

  const { column, direction } = getState().sort;
  if (!column) return;

  const th = table.querySelector(`th[data-col="${column}"]`);
  if (!th) return;

  if (direction === 1) th.classList.add("sorted-desc");
  if (direction === 2) th.classList.add("sorted-asc");
}
