// ─── Состояния ─────────────────────────────────────────

const _state = {
  timeframe: "1h",
  indicator: "RSI",   // RSI | MACD | EMA_SMA | VOLUME
  correlation: 1,
  sigtype: "all",     // all | strong | combined
  topN: 5,
  sort: {
    column: null,
    direction: 0,     // 0 = none, 1 = desc, 2 = asc
  },
};

export function getState() {
  return _state;
}

export function setState(patch) {
  Object.assign(_state, patch);
}

export function setSortState(column) {
  if (_state.sort.column === column) {
    _state.sort.direction++;

    if (_state.sort.direction > 2) {
      _state.sort.column = null;
      _state.sort.direction = 0;
    }

  } else {
    _state.sort.column = column;
    _state.sort.direction = 1;
  }
}
