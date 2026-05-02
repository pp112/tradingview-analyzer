// ─── Отрисовка таблицы ────────────────────────────────────────────────────

import { getState } from "./state.js";
import { getSignals } from "./signals.js";
import { applySorting, updateSortCell } from "./sorting.js";

// ── Главная функция отрисовки ──────────────────────────────────────────────

export function renderTable() {
  const tbody    = document.getElementById("signalBody");
  const thead    = document.querySelector("#signalTable thead tr");
  const state    = getState();
  const isVolume = state.indicator === "VOLUME";

  thead.innerHTML = buildHeader(isVolume);

  let rows = getSignals(state.timeframe);

  if (!isVolume) {
    rows = rows.filter(s => s.indicator === state.indicator);
  }

  rows = rows.filter(s => s.correlation <= state.correlation);
  rows = applySorting(rows);

  const hasRows = rows.length > 0;

  if (hasRows) {
    tbody.innerHTML = rows.map(buildRow).join("");
  } else {
    tbody.innerHTML = `<tr><td colspan="8" class="loading-cell">Нет данных для выбранных фильтров</td></tr>`;
  }

  updateSortCell();
}

// ── Шапка таблицы ─────────────────────────────────────────────────────────

function buildHeader(isVolume) {
  return `
    <th class="th-fav">★</th>
    <th data-col="symbol">Монета<span class="sort-icon"></span></th>
    <th data-col="indicator_value">Значение<span class="sort-icon"></span></th>
    <th data-col="indicator">Индикатор<span class="sort-icon"></span></th>
    ${!isVolume ? '<th data-col="direction">Направление<span class="sort-icon"></span></th>' : ""}
    <th data-col="correlation">Корреляция<span class="sort-icon"></span></th>
    <th>Подробно</th>
  `;
}

// ── Строка таблицы ─────────────────────────────────────────────────────────

function buildRow(signal, i) {
  const { valueCell, indicatorCell, directionCell } = buildCells(signal);

  return `
    <tr style="animation-delay:${i * 0.03}s">
      <td class="th-fav">☆</td>
      <td class="sym-cell">${signal.symbol}</td>
      <td>${valueCell}</td>
      <td>${indicatorCell}</td>
      ${directionCell}
      <td>${signal.correlation}</td>
      <td>𓏬</td>
    </tr>
  `;
}

// ── Ячейки в зависимости от типа индикатора ────────────────────────────────

function buildCells(signal) {
  if (getState().indicator === "VOLUME") {
    return buildVolumeCells(signal);
  }
  return buildIndicatorCells(signal);
}

function buildVolumeCells(signal) {
  const cls = signal.vol_ratio >= 4 ? "vol-red"
            : signal.vol_ratio >= 3 ? "vol-orange"
            : signal.vol_ratio >= 2 ? "vol-yellow"
            : "vol-default";

  return {
    valueCell:     `<span class="vol-cell ${cls}">${signal.vol_ratio}</span>`,
    indicatorCell: `<span class="badge badge-volume">VOLUME</span>`,
    directionCell: "",
  };
}

function buildIndicatorCells(signal) {
  const isBull    = signal.direction === "ВВЕРХ";
  const clsValue  = isBull ? "value-bull" : "value-bear";
  const clsBadge  = isBull ? "badge-bull"  : "badge-bear";

  return {
    valueCell:     `<span class="${clsValue}">${signal.indicator_value}</span>`,
    indicatorCell: `<span class="badge ${clsBadge}">${signal.indicator}</span>`,
    directionCell: `<td><span class="badge ${clsBadge}">${signal.direction}</span></td>`,
  };
}
