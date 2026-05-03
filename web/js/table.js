// ─── Отрисовка таблицы ────────────────────────────────────────────────────

import { getState } from "./state.js";
import { getSignals } from "./signals.js";

// ── Главная функция отрисовки ──────────────────────────────────────────────

export function renderTable() {
  const tbody    = document.getElementById("signalBody");
  const thead    = document.querySelector("#signalTable thead tr");
  const state    = getState();
  const isVolume = state.indicator === "vol_ratio";

  thead.innerHTML = buildHeader();

  let rows = getSignals(state.timeframe);

  if (!isVolume && state.sigtype === "all") {
    rows = rows.filter(s => s.indicator === state.indicator);
  }

  rows = rows.filter(s => s.correlation <= state.correlation);
  rows = filterBySignalType(rows);
  rows = sortByColumn(rows);

  const hasRows = rows.length > 0;

  if (hasRows) {
    tbody.innerHTML = rows.map(buildRow).join("");
  } else {
    const colCount = document.querySelectorAll("#signalTable thead th").length;
    tbody.innerHTML = `<tr><td colspan="8" class="loading-cell">Нет данных для выбранных фильтров</td></tr>`;
  }

  updateSortCell();
}

// ── Фильтрация по типу сигнала ────────────────────────────────────────────

function filterBySignalType(rows) {
  const { sigtype, topN } = getState();

  if (sigtype === "all") return rows;

  if (sigtype === "strong") {
    const topByIndicator = (type) =>
      rows
        .filter(row => row.indicator === type)
        .sort((a, b) => b.indicator_value - a.indicator_value)
        .slice(0, topN);

    return [
      ...topByIndicator("rsi"), 
      ...topByIndicator("macd"), 
      ...topByIndicator("ema_sma")
    ];
  }

  if (sigtype === "combined") {
    const countBySymbol = {};
    rows.forEach(row => {
      countBySymbol[row.symbol] = (countBySymbol[row.symbol] || 0) + 1;
    });
    const combined = rows.filter(row => countBySymbol[row.symbol] >= 2);

    const grouped = {};
    combined.forEach(row => {
      if (!grouped[row.symbol]) {
        grouped[row.symbol] = { 
          symbol:      row.symbol, 
          direction:   row.direction,
          rsi:         null, 
          macd:        null, 
          ema_sma:     null,
          vol_ratio:   row.vol_ratio,
          correlation: row.correlation
        };
      }
      grouped[row.symbol][row.indicator] = row.indicator_value;
    });

    return Object.values(grouped);
  }
}

// ── Сортировка ────────────────────────────────────────────────────────────

function sortByColumn(rows) {
  const { column, direction } = getState().sort;

  if (!column || direction === 0) return rows;

  const order = direction === 1 ? -1 : 1;

  const sortedRows = [...rows];
  console.log(column)
  sortedRows.sort((a, b) => {
    const v1 = a[column];
    const v2 = b[column];

    if (v1 === null) return 1;
    if (v2 === null) return -1;

    if (typeof v1 === "string") {
      return v1.localeCompare(v2) * order;
    }

    return (v1 - v2) * order;
  });

  return sortedRows;
}

// ── Обновление CSS-классов заголовков таблицы ─────────────────────────────

function updateSortCell() {
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

// ── Шапка таблицы ─────────────────────────────────────────────────────────

function buildHeader() {
  const { indicator, sigtype } = getState();

  if (sigtype === "combined") {
    return `
      <th class="th-fav">★</th>
      <th data-col="symbol">Монета<span class="sort-icon"></span></th>
      <th data-col="rsi">RSI<span class="sort-icon"></span></th>
      <th data-col="macd">MACD<span class="sort-icon"></span></th>
      <th data-col="ema_sma">EMA-SMA<span class="sort-icon"></span></th>
      <th data-col="direction">Направление<span class="sort-icon"></span></th>
      <th data-col="vol_ratio">VOLUME<span class="sort-icon"></span></th>
      <th data-col="correlation">Корреляция<span class="sort-icon"></span></th>
      <th>Подробно</th>
    `;
  }

  const isVolume = indicator === "vol_ratio";
  const indicator_value = isVolume ? "vol_ratio" : "indicator_value";
  
  return `
    <th class="th-fav">★</th>
    <th data-col="symbol">Монета<span class="sort-icon"></span></th>
    <th data-col="${indicator_value}">Значение<span class="sort-icon"></span></th>
    <th data-col="indicator">Индикатор<span class="sort-icon"></span></th>
    ${isVolume ? "" : '<th data-col="direction">Направление<span class="sort-icon"></span></th>'}
    ${isVolume ? "" : '<th data-col="vol_ratio">Объем<span class="sort-icon"></span></th>'}
    <th data-col="correlation">Корреляция<span class="sort-icon"></span></th>
    <th>Подробно</th>
  `;
}

// ── Строка таблицы ─────────────────────────────────────────────────────────

function buildRow(signal, i) {
  const { sigtype } = getState();

  if (sigtype === "combined") {
    return buildCombinedRow(signal, i);
  }

  return `
    <tr style="animation-delay:${i * 0.03}s">
      <td class="th-fav">☆</td>
      <td class="sym-cell">${signal.symbol}</td>
      ${buildIndicatorCells(signal)}
      <td>${signal.correlation}</td>
      <td>𓏬</td>
    </tr>
  `;
}

// ── Строка для комбинированных сигналов ────────────────────────────────────

function buildCombinedRow(signal, i) {
  const isBull    = signal.direction === "ВВЕРХ";
  const clsBadge  = isBull ? "badge-bull"  : "badge-bear";
  const clsValue  = isBull ? "value-bull" : "value-bear";
  const clsVolume = signal.vol_ratio >= 4 ? "vol-red"
                  : signal.vol_ratio >= 3 ? "vol-orange"
                  : signal.vol_ratio >= 2 ? "vol-yellow"
                  : "vol-default";
  
  const cell = (value) => value !== null
    ? `<span class="${clsValue}">${value}</span>`
    : `<span class="muted">-</span>`;

  return `
    <tr style="animation-delay:${i * 0.03}s">
      <td class="th-fav">☆</td>
      <td class="sym-cell">${signal.symbol}</td>
      <td>${cell(signal.rsi)}</td>
      <td>${cell(signal.macd)}</td>
      <td>${cell(signal.ema_sma)}</td>
      <td><span class="badge ${clsBadge}">${signal.direction}</span></td>
      <td><span class="vol-cell ${clsVolume}">${signal.vol_ratio}</span></td>
      <td><span class="corr-cell">${signal.correlation}</td>
      <td>𓏬</td>
    </tr>
  `;
}

// ── Внешний вид ячеек в зависимости от типа индикатора ─────────────────────

function buildIndicatorCells(signal) {
  const isVolume  = getState().indicator === "vol_ratio";
  const clsVolume = signal.vol_ratio >= 4 ? "vol-red"
                  : signal.vol_ratio >= 3 ? "vol-orange"
                  : signal.vol_ratio >= 2 ? "vol-yellow"
                  : "vol-default";

  if (isVolume) {
    return `
      <td><span class="vol-cell ${clsVolume}">${signal.vol_ratio}</span></td>
      <td><span class="badge badge-volume">VOLUME</span></td>
    `
  }

  const isBull    = signal.direction === "ВВЕРХ";
  const clsValue  = isBull ? "value-bull" : "value-bear";
  const clsBadge  = isBull ? "badge-bull"  : "badge-bear";
  const indicator = signal.indicator.toUpperCase().replace("_", "-")

  return `
    <td><span class="${clsValue}">${signal.indicator_value}</span></td>
    <td><span class="badge ${clsBadge}">${indicator}</span></td>
    <td><span class="badge ${clsBadge}">${signal.direction}</span></td>
    <td><span class="vol-cell ${clsVolume}">${signal.vol_ratio}</span></td>
  `
}
