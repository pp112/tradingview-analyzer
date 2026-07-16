// ─── Состояния ─────────────────────────────────────────

const _state = {
  timeframe: "1h",
  indicator: "rsi",   // rsi | macd | ema_sma | vol_ratio | null
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
  const currentState = getState();
  const currentIndicator = currentState.indicator;
  const currentSort = currentState.sort;
  if ((currentIndicator === "macd" || currentIndicator === "ema_sma") && column === "indicator_value") {
    if (currentSort.column === column) {

      if (currentSort.direction === 1) {
        _state.sort.direction = 0;
        _state.sort.column = null;
      } else {
        _state.sort.direction = 1;
      }
    } else {
      _state.sort.column = column;
      _state.sort.direction = 1;
    }
  } else {
    if (currentSort.column === column) {
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
}
