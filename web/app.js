/* ── CryptoScope Dashboard — app.js ──────────────────────────────────────── */

const API = 'http://localhost:8000/api';

/* ── State ────────────────────────────────────────────────────────────────── */
const state = {
  tf: '1h',
  count: 20,
  signals: [],
  favs: new Set(JSON.parse(localStorage.getItem('cs_favs') || '[]')),
  search: '',
  pollTimer: null,
};

/* ── DOM refs ─────────────────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);
const signalBody  = $('signalBody');
const updateText  = $('updateText');
const corrList    = $('corrList');
const searchInput = $('searchInput');
const modalOverlay = $('modalOverlay');
const modalTitle   = $('modalTitle');
const modalBody    = $('modalBody');

/* ── Init ─────────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  bindNav();
  bindTF();
  bindCount();
  bindSearch();
  bindModal();
  bindMenu();
  duplicateTicker();
  loadSignals();
  loadCorrelations();
  startPolling();
});

/* ── Navigation ───────────────────────────────────────────────────────────── */
function bindNav() {
  document.querySelectorAll('.nav-item').forEach(el => {
    el.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
      el.classList.add('active');
      // Close sidebar on mobile
      if (window.innerWidth <= 900) $('sidebar').classList.remove('open');
    });
  });
  // Card links that switch nav
  document.querySelectorAll('[data-page]').forEach(el => {
    el.addEventListener('click', () => {
      const target = document.querySelector(`.nav-item[data-page="${el.dataset.page}"]`);
      if (target) target.click();
    });
  });
}

function bindMenu() {
  $('menuBtn').addEventListener('click', () => {
    $('sidebar').classList.toggle('open');
  });
}

/* ── TF & Count ───────────────────────────────────────────────────────────── */
function bindTF() {
  $('tfButtons').addEventListener('click', e => {
    const btn = e.target.closest('.tf-btn');
    if (!btn) return;
    document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.tf = btn.dataset.tf;
    loadSignals();
  });
}

function bindCount() {
  $('countButtons').addEventListener('click', e => {
    const btn = e.target.closest('.count-btn');
    if (!btn) return;
    document.querySelectorAll('.count-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.count = parseInt(btn.dataset.n);
    renderTable();
  });
}

/* ── Search ───────────────────────────────────────────────────────────────── */
function bindSearch() {
  searchInput.addEventListener('input', () => {
    state.search = searchInput.value.trim().toLowerCase();
    renderTable();
  });
}

/* ── Load signals ─────────────────────────────────────────────────────────── */
async function loadSignals() {
  setTableLoading(true);
  try {
    const res = await fetch(`${API}/signals/${state.tf}`);
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    state.signals = data.signals || [];
    const ago = data.updated_minutes_ago;
    updateText.textContent = ago != null ? `обновлено ${ago}м назад` : 'данные актуальны';
    renderTable();
  } catch (err) {
    console.warn('API недоступен, показываю demo-данные:', err.message);
    state.signals = DEMO_SIGNALS;
    updateText.textContent = 'demo-режим';
    renderTable();
  }
}

async function loadCorrelations() {
  try {
    const res = await fetch(`${API}/correlations`);
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    renderCorrelations(data.correlations.slice(0, 8));
  } catch {
    renderCorrelations(DEMO_CORR);
  }
}

/* ── Polling ──────────────────────────────────────────────────────────────── */
function startPolling() {
  const intervals = { '15m': 60, '30m': 120, '1h': 300, '4h': 600, '1d': 1800 };
  clearInterval(state.pollTimer);
  state.pollTimer = setInterval(() => {
    loadSignals();
    loadCorrelations();
  }, (intervals[state.tf] || 300) * 1000);
}

/* ── Render table ─────────────────────────────────────────────────────────── */
function setTableLoading(on) {
  if (on) {
    signalBody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:36px;color:var(--text2);">
      <span class="loader"></span> Загрузка сигналов...
    </td></tr>`;
  }
}

function renderTable() {
  let rows = state.signals;

  // search filter
  if (state.search) {
    rows = rows.filter(r => r.symbol.toLowerCase().includes(state.search));
  }

  // limit
  rows = rows.slice(0, state.count);

  if (!rows.length) {
    signalBody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:36px;color:var(--text2);">
      Сигналов не найдено
    </td></tr>`;
    return;
  }

  signalBody.innerHTML = rows.map((r, i) => buildRow(r, i)).join('');

  // bind fav buttons
  signalBody.querySelectorAll('.fav-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const sym = btn.dataset.sym;
      state.favs.has(sym) ? state.favs.delete(sym) : state.favs.add(sym);
      localStorage.setItem('cs_favs', JSON.stringify([...state.favs]));
      btn.classList.toggle('active');
      btn.textContent = state.favs.has(sym) ? '★' : '☆';
    });
  });

  // bind chart buttons
  signalBody.querySelectorAll('.chart-btn').forEach(btn => {
    btn.addEventListener('click', () => openModal(btn.dataset.sym));
  });
}

function buildRow(r, i) {
  const sym = r.symbol.replace('.P','').replace('USDT','/USDT');
  const isFav = state.favs.has(r.symbol);

  // RSI
  let rsiHtml = '<span class="rsi-mid">—</span>';
  if (r.rsi != null) {
    const cls = r.rsi > 70 ? 'rsi-bear' : r.rsi < 30 ? 'rsi-bull' : 'rsi-mid';
    rsiHtml = `<span class="${cls}">${r.rsi.toFixed(1)}</span>`;
  }

  // Indicator badge
  const indCls = r.bull === true ? 'badge-bull' : r.bull === false ? 'badge-bear' : 'badge-blue';
  const indHtml = `<span class="badge ${indCls}">${r.indicator || '—'}</span>`;

  // Direction badge
  const dirCls = r.direction === 'ВВЕРХ' ? 'badge-up' : r.direction === 'ВНИЗ' ? 'badge-down' : 'badge-blue';
  const dirHtml = `<span class="badge ${dirCls}">${r.direction || '—'}</span>`;

  // EMA/SMA
  const emaSma = r.ema_sma || '—';
  const emaCls = emaSma.includes('>') ? 'pos' : emaSma.includes('<') ? 'neg' : '';

  // Vol ratio
  const vol = r.vol_ratio != null ? r.vol_ratio.toFixed(2) : '—';
  const volCls = r.vol_ratio > 2 ? 'pos' : r.vol_ratio < 0.5 ? 'neg' : '';

  return `
  <tr style="animation-delay:${i * 0.03}s">
    <td class="th-fav">
      <button class="fav-btn ${isFav ? 'active' : ''}" data-sym="${r.symbol}">
        ${isFav ? '★' : '☆'}
      </button>
    </td>
    <td class="sym-cell">${sym}</td>
    <td>${rsiHtml}</td>
    <td>${indHtml}</td>
    <td>${dirHtml}</td>
    <td class="ema-sma-cell ${emaCls}">${emaSma}</td>
    <td class="vol-cell ${volCls}">${vol}</td>
    <td class="tf-cell">${r.timeframe || state.tf}</td>
    <td><button class="chart-btn" data-sym="${r.symbol}">↗</button></td>
  </tr>`;
}

/* ── Render correlations ──────────────────────────────────────────────────── */
function renderCorrelations(items) {
  if (!items || !items.length) {
    corrList.innerHTML = '<div class="corr-loading">Нет данных</div>';
    return;
  }
  corrList.innerHTML = items.map(item => {
    const val = typeof item.corr === 'number' ? item.corr : item;
    const sym = item.symbol || item;
    const pct = Math.abs(val) * 100;
    const color = val >= 0.7 ? 'var(--green)' : val >= 0.3 ? 'var(--blue)' : 'var(--red)';
    const symClean = String(sym).replace('.P','').replace('USDT','/USDT');
    return `
    <div class="corr-row">
      <span class="corr-sym">${symClean}</span>
      <div class="corr-bar-wrap">
        <div class="corr-bar">
          <div class="corr-fill" style="width:${pct}%;background:${color};"></div>
        </div>
      </div>
      <span class="corr-val" style="color:${color}">${val.toFixed(2)}</span>
    </div>`;
  }).join('');
}

/* ── Modal ────────────────────────────────────────────────────────────────── */
function bindModal() {
  $('modalClose').addEventListener('click', closeModal);
  modalOverlay.addEventListener('click', e => { if (e.target === modalOverlay) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
}

async function openModal(symbol) {
  modalTitle.textContent = symbol.replace('.P','').replace('USDT','/USDT');
  modalBody.innerHTML = '<div style="color:var(--text2);padding:12px 0;"><span class="loader"></span> Загрузка...</div>';
  modalOverlay.classList.add('open');

  try {
    const res = await fetch(`${API}/indicators/${state.tf}/${symbol}`);
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    renderModal(data.indicators);
  } catch {
    // find in already-loaded signals
    const sig = state.signals.find(s => s.symbol === symbol);
    if (sig) renderModalFromSignal(sig);
    else modalBody.innerHTML = '<div style="color:var(--text2);">Данные недоступны</div>';
  }
}

function renderModal(ind) {
  if (!ind) { modalBody.innerHTML = '<div style="color:var(--text2);">Нет данных</div>'; return; }
  const rsi = ind.rsi != null ? ind.rsi.toFixed(2) : '—';
  const macd = ind.macd?.curr;
  const macdVal  = macd ? macd.MACD.toFixed(4) : '—';
  const macdSig  = macd ? macd.MACD_signal.toFixed(4) : '—';
  const ema = ind.ema ? ind.ema[1].toFixed(4) : '—';
  const sma = ind.sma ? ind.sma[1].toFixed(4) : '—';
  const vol = ind.volume?.ratio != null ? ind.volume.ratio.toFixed(2) : '—';

  const rsiCls = ind.rsi > 70 ? 'var(--red)' : ind.rsi < 30 ? 'var(--green)' : 'var(--blue)';

  modalBody.innerHTML = `
  <div class="modal-grid">
    <div class="modal-metric">
      <div class="m-label">RSI (14)</div>
      <div class="m-val" style="color:${rsiCls}">${rsi}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">Vol Ratio</div>
      <div class="m-val">${vol}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">MACD</div>
      <div class="m-val">${macdVal}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">MACD Signal</div>
      <div class="m-val">${macdSig}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">EMA</div>
      <div class="m-val">${ema}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">SMA</div>
      <div class="m-val">${sma}</div>
    </div>
  </div>`;
}

function renderModalFromSignal(sig) {
  modalBody.innerHTML = `
  <div class="modal-grid">
    <div class="modal-metric">
      <div class="m-label">RSI</div>
      <div class="m-val" style="color:${sig.rsi > 70 ? 'var(--red)' : sig.rsi < 30 ? 'var(--green)' : 'var(--blue)'}">${sig.rsi != null ? sig.rsi.toFixed(2) : '—'}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">MACD Diff</div>
      <div class="m-val">${sig.macd_diff != null ? sig.macd_diff.toFixed(4) : '—'}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">EMA / SMA</div>
      <div class="m-val" style="font-size:0.8rem">${sig.ema_sma || '—'}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">Vol Ratio</div>
      <div class="m-val">${sig.vol_ratio != null ? sig.vol_ratio.toFixed(2) : '—'}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">Сигнал</div>
      <div class="m-val" style="font-size:0.75rem;color:${sig.bull ? 'var(--green)' : 'var(--red)'}">${sig.signal}</div>
    </div>
    <div class="modal-metric">
      <div class="m-label">Таймфрейм</div>
      <div class="m-val">${sig.timeframe}</div>
    </div>
  </div>`;
}

function closeModal() {
  modalOverlay.classList.remove('open');
}

/* ── Ticker duplication for seamless loop ─────────────────────────────────── */
function duplicateTicker() {
  const track = $('tickerTrack');
  track.innerHTML += track.innerHTML; // duplicate for seamless scroll
}

/* ── Demo data (fallback when API offline) ────────────────────────────────── */
const DEMO_SIGNALS = [
  {symbol:'BTCUSDT.P',  signal:'RSI_OVERBOUGHT', indicator:'RSI',     direction:'ВНИЗ',  bull:false, rsi:82.6, macd_diff:0.042, ema_sma:'EMA > SMA', vol_ratio:1.82, timeframe:'1h'},
  {symbol:'ETHUSDT.P',  signal:'RSI_OVERBOUGHT', indicator:'RSI',     direction:'ВНИЗ',  bull:false, rsi:79.3, macd_diff:0.031, ema_sma:'EMA > SMA', vol_ratio:1.42, timeframe:'1h'},
  {symbol:'SOLUSDT.P',  signal:'RSI_OVERSOLD',   indicator:'RSI',     direction:'ВВЕРХ', bull:true,  rsi:18.7, macd_diff:0.078, ema_sma:'EMA < SMA', vol_ratio:2.15, timeframe:'1h'},
  {symbol:'XRPUSDT.P',  signal:'RSI_OVERSOLD',   indicator:'RSI',     direction:'ВВЕРХ', bull:true,  rsi:19.2, macd_diff:0.055, ema_sma:'EMA < SMA', vol_ratio:1.91, timeframe:'1h'},
  {symbol:'DOGEUSDT.P', signal:'MACD_BULLISH',    indicator:'MACD',    direction:'ВВЕРХ', bull:true,  rsi:81.4, macd_diff:0.124, ema_sma:'EMA > SMA', vol_ratio:3.44, timeframe:'1h'},
  {symbol:'ADAUSDT.P',  signal:'MACD_BEARISH',    indicator:'MACD',    direction:'ВНИЗ',  bull:false, rsi:17.9, macd_diff:0.067, ema_sma:'EMA < SMA', vol_ratio:1.22, timeframe:'1h'},
  {symbol:'LINKUSDT.P', signal:'EMA_SMA_BULLISH', indicator:'EMA/SMA', direction:'ВВЕРХ', bull:true,  rsi:83.7, macd_diff:0.033, ema_sma:'EMA > SMA', vol_ratio:2.88, timeframe:'1h'},
  {symbol:'MATICUSDT.P',signal:'EMA_SMA_BULLISH', indicator:'EMA/SMA', direction:'ВВЕРХ', bull:true,  rsi:84.1, macd_diff:0.021, ema_sma:'EMA > SMA', vol_ratio:1.67, timeframe:'1h'},
  {symbol:'BNBUSDT.P',  signal:'RSI_OVERBOUGHT',  indicator:'RSI',     direction:'ВНИЗ',  bull:false, rsi:75.2, macd_diff:0.019, ema_sma:'EMA > SMA', vol_ratio:1.33, timeframe:'1h'},
  {symbol:'AVAXUSDT.P', signal:'MACD_BEARISH',    indicator:'MACD',    direction:'ВНИЗ',  bull:false, rsi:22.1, macd_diff:0.088, ema_sma:'EMA < SMA', vol_ratio:2.61, timeframe:'1h'},
  {symbol:'SUIUSDT.P',  signal:'RSI_OVERSOLD',    indicator:'RSI',     direction:'ВВЕРХ', bull:true,  rsi:16.4, macd_diff:0.102, ema_sma:'EMA < SMA', vol_ratio:4.12, timeframe:'1h'},
  {symbol:'ARBUSDT.P',  signal:'EMA_SMA_BEARISH', indicator:'EMA/SMA', direction:'ВНИЗ',  bull:false, rsi:28.8, macd_diff:0.014, ema_sma:'EMA < SMA', vol_ratio:1.05, timeframe:'1h'},
];

const DEMO_CORR = [
  {symbol:'ETHUSDT.P',  corr:0.96},
  {symbol:'BNBUSDT.P',  corr:0.91},
  {symbol:'SOLUSDT.P',  corr:0.88},
  {symbol:'AVAXUSDT.P', corr:0.84},
  {symbol:'LINKUSDT.P', corr:0.79},
  {symbol:'ADAUSDT.P',  corr:0.73},
  {symbol:'ARBUSDT.P',  corr:0.61},
  {symbol:'DOGEUSDT.P', corr:0.44},
];
