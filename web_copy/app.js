const signals = {
  "1h": [{ symbol: "ETH/USDT", indicator: "RSI", indicator_value: 76.06, direction: "ВНИЗ", vol_ratio: 1.5, correlation: 0.91, timeframe: "1h" },
         { symbol: "ZBT/USDT", indicator: "RSI", indicator_value: 70.52, direction: "ВНИЗ", vol_ratio: 2.2, correlation: 0.7, timeframe: "1h" },
         { symbol: "LDO/USDT", indicator: "RSI", indicator_value: 88.39, direction: "ВНИЗ", vol_ratio: 3.5, correlation: 0.65, timeframe: "1h" },
         { symbol: "LDO/USDT", indicator: "RSI", indicator_value: 88.39, direction: "ВНИЗ", vol_ratio: 4.5, correlation: 0.65, timeframe: "1h" }
  ],
  "4h": [{ symbol: "KAT/USDT", indicator: "RSI", indicator_value: 28.08, direction: "ВВЕРХ", vol_ratio: 12.13, correlation: -0.83, timeframe: "4h" },
         { symbol: "OPG/USDT", indicator: "MACD", indicator_value: 0.0793723991114607, direction: "ВВЕРХ", vol_ratio: 12.13, correlation: 0.77, timeframe: "4h" }
  ],
  "30m": [{ symbol: "XAU/USDT", indicator: "EMA_SMA", indicator_value: 0.08799516178896738, direction: "ВВЕРХ", vol_ratio: 12.13, correlation: 0.6, timeframe: "30m" },
          { symbol: "PIPPIN/USDT", indicator: "EMA_SMA", indicator_value: 5.586622931205015e-6, direction: "ВНИЗ", vol_ratio: 12.13, correlation: -0.72, timeframe: "30m" },
          { symbol: "NAORIS/USDT", indicator: "RSI", indicator_value: 81.25, direction: "ВНИЗ", vol_ratio: 12.13, correlation: 0.73, timeframe: "30m" }
  ]
};

const API = "http://localhost:8000";

// const signals = {};

const state = {
  timeframe: "1h",
  indicator: "RSI", // RSI, MACD, EMA_SMA, VOLUME
  correlation: 1,
  sort: {
    column: null,
    direction: 0
  }
};


document.addEventListener("DOMContentLoaded", () => {
  initControls();
  initCorrelationInput();
  connectSSE();
  renderTable();
});


function bindToggle(containerId, selector, statekey, datakey) {
  document.getElementById(containerId).addEventListener("click", (e) => {
    const btn = e.target.closest(selector);

    document.querySelectorAll(selector).forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    
    state[statekey] = btn.dataset[datakey];
    renderTable();
  });
}

function initControls() {
  bindToggle("tfButtons", ".btn--tf", "timeframe", "tf");
  bindToggle("indicatorButtons", ".btn--indicator", "indicator", "ind");
}


function initCorrelationInput() {
  const input = document.getElementById("corrInput");
  const plus = document.getElementById("corrPlus");
  const minus = document.getElementById("corrMinus");

  const clamp = (v) => Math.max(-1, Math.min(1, v));

  function update(val) {
    state.correlation = clamp(val);
    input.value = state.correlation.toFixed(2).replace(/\.00$/, "");
    renderTable();
  }

  plus.addEventListener("click", () => update(state.correlation + 0.05));
  minus.addEventListener("click", () => update(state.correlation - 0.05));

  input.addEventListener("input", () => {
    const val = parseFloat(input.value.replace(",", "."));
    if (isNaN(val)) return;

    state.correlation = clamp(val);
    renderTable();
  });

  input.addEventListener("blur", () => update(state.correlation));
  input.addEventListener("focus", () => input.select());
}


function connectSSE() {
  const eventSource = new EventSource(`${API}/stream`);

  eventSource.addEventListener("update", (event) => {
    const data = JSON.parse(event.data);
    console.log(`Пришло сообщение обновления: ${data.timeframe}`);
    fetchSignals(data.timeframe);
  });
}

async function fetchSignals(tf) {
  const res = await fetch(`${API}/signals?tf=${tf}`);
  const data = await res.json();

  setSignals(tf, data);
  console.log(`Данные обновлены: ${tf}`);
  
  if (tf === state.timeframe) {
    renderTable();
  }
}

function setSignals(tf, data) {
  signals[tf] = data.map(formatSignal);
}

function formatSignal(signal) {
  return {
    ...signal,
    symbol: signal.symbol.replace(".P", ""),
    indicator_value: Number(signal.indicator_value.toFixed(2)),
    vol_ratio: Number(signal.vol_ratio.toFixed(2))
  };
}


function renderTable() {
  const tbody = document.getElementById("signalBody");
  const thead = document.querySelector("#signalTable thead tr");
  
  const isVolume = state.indicator === "VOLUME";

  thead.innerHTML = `
    <th class="th-fav">★</th>
    <th data-col="symbol">Монета<span class="sort-icon"></span></th>
    <th data-col="indicator_value">Значение<span class="sort-icon"></span></th>
    <th data-col="indicator">Индикатор<span class="sort-icon"></span></th>
    ${!isVolume ? '<th data-col="direction">Направление<span class="sort-icon"></span></th>' : ""}
    <th data-col="correlation">Корреляция<span class="sort-icon"></span></th>
    <th>Подробно</th>
  `;

  let rows = signals[state.timeframe] || [];

  if (!isVolume) {
    rows = rows.filter(s => s.indicator === state.indicator);
  }

  rows = rows.filter(s => s.correlation <= state.correlation);

  tbody.innerHTML = rows.map((signal, i) => buildRow(signal, i)).join("");
}

function buildRow(signal, i) {
  let valueCell;
  let indicatorCell;
  let directionCell = "";

  if (state.indicator === "VOLUME") {
    const clsColor = signal.vol_ratio >= 4 
      ? "vol-red" 
      : signal.vol_ratio >= 3 
      ? "vol-orange" 
      : signal.vol_ratio >= 2 
      ? "vol-yellow" 
      : "vol-default";

    valueCell = `<span class="vol-cell ${clsColor}">${signal.vol_ratio}</span>`;
    indicatorCell = `<span class="badge badge-volume">VOLUME</span>`;

  } else {
    const clsValue = signal.direction === "ВВЕРХ" ? "value-bull" : "value-bear";
    const clsDirection = signal.direction === "ВВЕРХ" ? "badge-bull" : "badge-bear";

    valueCell = `<span class=${clsValue}>${signal.indicator_value}</span>`;
    indicatorCell = `<span class="badge ${clsDirection}">${signal.indicator}</span>`;
    directionCell = `<td><span class="badge ${clsDirection}">${signal.direction}</span></td>`;
  }
  
  return `
  <tr style="animation-delay:${i * 0.03}s">
    <td class="th-fav">☆</td>
    <td class="sym-cell">${signal.symbol}</td>
    <td>${valueCell}</td>
    <td>${indicatorCell}</td>
    ${directionCell}
    <td>${signal.correlation}</td>
    <td>𓏬</td>
  </tr>`;
}
