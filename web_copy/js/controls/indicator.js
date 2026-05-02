// ─── Переключатель индикатора ─────────────────────────────────────────────

import { getState, setState } from "../state.js";
import { renderTable } from "../table.js";

export function initIndicator() {
  const btns = document.getElementById("indicatorButtons");
  
  btns.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn--indicator");
    if (!btn) return;

    // Индикаторы недоступны при режиме "не все"
    if (getState().sigtype !== "all") return;

    btn.parentElement.querySelector(".active").classList.remove("active");
    btn.classList.add("active");

    setState({ indicator: btn.dataset.ind });
    renderTable();
  });
}
