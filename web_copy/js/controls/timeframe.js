// ─── Переключатель таймфрейма ─────────────────────────────────────────────

import { setState } from "../state.js";
import { renderTable } from "../table.js";

export function initTimeframe() {
  const btns = document.getElementById("tfButtons");

  btns.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn--tf");
    if (!btn) return;

    btn.parentElement.querySelector(".active").classList.remove("active");
    btn.classList.add("active");

    setState({ timeframe: btn.dataset.tf });
    renderTable();
  });
}
