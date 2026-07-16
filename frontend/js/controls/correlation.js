// ─── Поле ввода: корреляция ───────────────────────────────────────────────

import { getState, setState } from "../state.js";
import { renderTable } from "../table.js";

const clamp = (v) => Math.max(-1, Math.min(1, v));

export function initCorrelation() {
  const input = document.getElementById("corrInput");
  const plus  = document.getElementById("corrPlus");
  const minus = document.getElementById("corrMinus");

  function update(val) {
    const clamped = clamp(val);
    setState({ correlation: clamped });
    input.value = clamped.toFixed(2).replace(/\.00$/, "");
    renderTable();
  }

  plus.addEventListener("click",  () => update(getState().correlation + 0.05));
  minus.addEventListener("click", () => update(getState().correlation - 0.05));

  input.addEventListener("input", () => {
    const v = parseFloat(input.value.replace(",", "."));
    if (!isNaN(v)) {
      setState({ correlation: clamp(v) });
    }
  });

  input.addEventListener("blur", () => update(getState().correlation));
}
