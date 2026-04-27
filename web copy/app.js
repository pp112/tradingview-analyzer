const signals = [
  { symbol: "ETHUSDT.P", indicator: "RSI", indicator_value: 76.06, direction: "ВНИЗ", correlation: 0.91, timeframe: "1h" },
  { symbol: "ZBTUSDT.P", indicator: "RSI", indicator_value: 70.52, direction: "ВНИЗ", correlation: 0.7, timeframe: "1h" },
  { symbol: "LDOUSDT.P", indicator: "RSI", indicator_value: 88.39, direction: "ВНИЗ", correlation: 0.65, timeframe: "1h" },
  { symbol: "KATUSDT.P", indicator: "RSI", indicator_value: 28.08, direction: "ВВЕРХ", correlation: -0.83, timeframe: "1h" },
  { symbol: "OPGUSDT.P", indicator: "MACD", indicator_value: 0.0793723991114607, direction: "ВВЕРХ", correlation: 0.77, timeframe: "1h" },
  { symbol: "XAUUSDT.P", indicator: "EMA_SMA", indicator_value: 0.08799516178896738, direction: "ВВЕРХ", correlation: 0.6, timeframe: "1h" },
  { symbol: "PIPPINUSDT.P", indicator: "EMA_SMA", indicator_value: 5.586622931205015e-6, direction: "ВНИЗ", correlation: -0.72, timeframe: "4h" },
  { symbol: "NAORISUSDT.P", indicator: "RSI", indicator_value: 81.25, direction: "ВНИЗ", correlation: 0.73, timeframe: "4h" }
];

let currentTimeframe = "1h";

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
    <td class="fav-btn">☆</td>
    <td class="sym-cell">${signal.symbol}</td>
    <td>${indValue}</td>
    <td>${indName}</td>
    <td>${indDirection}</td>
    <td>${signal.correlation}</td>
    <td>𓏬</td>
  </tr>`;
}

renderTable();