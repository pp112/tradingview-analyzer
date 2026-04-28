// const signals = [
//   { symbol: "ETHUSDT.P", indicator: "RSI", indicator_value: 76.06, direction: "ВНИЗ", correlation: 0.91, timeframe: "1h" },
//   { symbol: "ZBTUSDT.P", indicator: "RSI", indicator_value: 70.52, direction: "ВНИЗ", correlation: 0.7, timeframe: "1h" },
//   { symbol: "LDOUSDT.P", indicator: "RSI", indicator_value: 88.39, direction: "ВНИЗ", correlation: 0.65, timeframe: "1h" },
//   { symbol: "KATUSDT.P", indicator: "RSI", indicator_value: 28.08, direction: "ВВЕРХ", correlation: -0.83, timeframe: "1h" },
//   { symbol: "OPGUSDT.P", indicator: "MACD", indicator_value: 0.0793723991114607, direction: "ВВЕРХ", correlation: 0.77, timeframe: "1h" },
//   { symbol: "XAUUSDT.P", indicator: "EMA_SMA", indicator_value: 0.08799516178896738, direction: "ВВЕРХ", correlation: 0.6, timeframe: "1h" },
//   { symbol: "PIPPINUSDT.P", indicator: "EMA_SMA", indicator_value: 5.586622931205015e-6, direction: "ВНИЗ", correlation: -0.72, timeframe: "4h" },
//   { symbol: "NAORISUSDT.P", indicator: "RSI", indicator_value: 81.25, direction: "ВНИЗ", correlation: 0.73, timeframe: "4h" }
// ];

const API = "http://localhost:8000"

const signals = [];

let currentTimeframe = "1h";


document.addEventListener("DOMContentLoaded", () => {
  bindTF();
  connectSSE();
  renderTable();
})


function bindTF() {
  document.getElementById("tfButtons").addEventListener("click", e => {
    const btn = e.target.closest(".tf-btn");
    document.querySelectorAll(".tf-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentTimeframe = btn.dataset.tf;
    renderTable();
  })
}


function connectSSE() {
  const eventSource = new EventSource(`${API}/stream`);

  eventSource.addEventListener("update", (event) => {
    const data = JSON.parse(event.data);
    console.log(`Пришло сообщение обновления: ${data.timeframe}`);
    fetchSignals(data.timeframe);
  })
}

async function fetchSignals(tf) {
  const res = await fetch(`${API}/signals?tf=${tf}`);
  const data = await res.json();
  setSignals(tf, data);
  console.log(`Данные обновлены: ${tf}`);
  if (tf === currentTimeframe) {
    renderTable();
  }
}

function setSignals(tf, data) {
  const formated = data.map(formatSignal);
  const filtered = signals.filter(x => x.timeframe !== tf);
  signals.length = 0;
  signals.push(...formated, ...filtered);
}

function formatSignal(signal) {
  return {
    ...signal,
    symbol: signal.symbol.replace(".P", ""),
    indicator_value: Number(signal.indicator_value.toFixed(2))
  };
}


function renderTable() {
  const tbody = document.getElementById("signalBody");
  
  let rows = signals.filter(x => x.timeframe === currentTimeframe);

  tbody.innerHTML = rows.map((signal, i) => buildRow(signal, i)).join("");
}

function buildRow(signal, i) {
  const clsValue = signal.direction === "ВВЕРХ" ? "value-bull" : "value-bear";
  const indValue = `<span class=${clsValue}>${signal.indicator_value}</span>`;
  
  const clsDirection = signal.direction === "ВВЕРХ" ? "badge-bull" : "badge-bear";
  const indName = `<span class="badge ${clsDirection}">${signal.indicator}</span>`;
  
  const indDirection = `<span class="badge ${clsDirection}">${signal.direction}</span>`
  
  return `
  <tr style="animation-delay:${i * 0.03}s">
    <td class="th-fav">☆</td>
    <td class="sym-cell">${signal.symbol}</td>
    <td>${indValue}</td>
    <td>${indName}</td>
    <td>${indDirection}</td>
    <td>${signal.correlation}</td>
    <td>𓏬</td>
  </tr>`;
}
