// ─── Поле ввода: количество сигналов ─────────────────────────────────────

import { getState, setState } from "../state.js";
import { renderTable } from "../table.js";

const clamp = (v) => Math.max(1, Math.min(50, v));

export function initTopN() {
  const input = document.getElementById("topNInput");
  const plus  = document.getElementById("topNPlus");
  const minus = document.getElementById("topNMinus");

  function update(val) {
    const clamped = clamp(val);
    setState({ topN: clamped });
    input.value = clamped;
    renderTable();
  }

  plus.addEventListener("click",  () => update(getState().topN + 1));
  minus.addEventListener("click", () => update(getState().topN - 1));

  input.addEventListener("input", () => {
    const v = parseInt(input.value);
    if (!isNaN(v)) {
      setState({ topN: clamp(v) });
    }
  });

  input.addEventListener("blur", () => update(getState().topN));
}
