// ─── Отрисовка карточек цен и объёмов ────────────────────────────────────

export function renderBottomCards(data) {
  _renderTopGainers(data);
  _renderTopLosers(data);
  _renderVolumeSpikes(data);
}

// ── Топ рост ─────────────────────────────────────────────────────────────

function _renderTopGainers(data) {
  const list = document.getElementById("topGainersList");

  const top = Object.entries(data)
    .filter(([_, values]) => values.price_delta_pct > 0)
    .sort((a, b) => b[1].price_delta_pct - a[1].price_delta_pct);

  list.innerHTML = top.map(([symbol, values], i) => {
    return `
      <div class="mover-row">
        <span class="mover-rank">${i + 1}</span>
        <span class="mover-sym">
          <a href="https://www.tradingview.com/chart/?symbol=BYBIT:${symbol.replace("/", "")}"
             target="_blank"
             class="sym-link">
            ${_formatSymbol(symbol)}
          </a>
        </span>
        <span class="mover-pct pos">+${values.price_delta_pct}%</span>
      </div>
    `;
  }).join("");
}

// ── Топ падение ──────────────────────────────────────────────────────────

function _renderTopLosers(data) {
  const list = document.getElementById("topLosersList");

  const top = Object.entries(data)
    .filter(([_, values]) => values.price_delta_pct < 0)
    .sort((a, b) => a[1].price_delta_pct - b[1].price_delta_pct);

  list.innerHTML = top.map(([symbol, values], i) => {
    return `
      <div class="mover-row">
        <span class="mover-rank">${i + 1}</span>
        <span class="mover-sym">
          <a href="https://www.tradingview.com/chart/?symbol=BYBIT:${symbol.replace("/", "")}"
             target="_blank"
             class="sym-link">
            ${_formatSymbol(symbol)}
          </a>
        </span>
        <span class="mover-pct neg">${values.price_delta_pct}%</span>
      </div>
    `;
  }).join("");
}

// ── Всплески объёма ──────────────────────────────────────────────────────

function _renderVolumeSpikes(data) {
  const list = document.getElementById("volumeSpikesList");

  const top = Object.entries(data)
    .filter(([_, values]) => values.volume_delta_pct !== 0)
    .sort((a, b) => b[1].volume_delta_pct - a[1].volume_delta_pct)

  list.innerHTML = top.map(([symbol, values], i) => {
    return `
      <div class="mover-row">
        <span class="mover-rank">${i + 1}</span>
        <span class="mover-sym">
          <a href="https://www.tradingview.com/chart/?symbol=BYBIT:${symbol.replace("/", "")}"
             target="_blank"
             class="sym-link">
            ${_formatSymbol(symbol)}
          </a>
        </span>
        <span class="mover-pct vol-pct">${values.volume_delta_pct}%</span>
      </div>
    `; 
  }).join("");
}

function _formatSymbol(symbol) {
  return symbol.replace("USDT", "/USDT").replace(".P", "");
}