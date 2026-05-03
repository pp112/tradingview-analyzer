// ─── Переключатель индикатора ─────────────────────────────────────────────

import { getState, setState } from "../state.js";
import { renderTable } from "../table.js";

export function initIndicator() {
  const btnsSigtype   = document.getElementById("sigtypeButtons");
  const btnsIndicator = document.getElementById("indicatorButtons");
  
  btnsIndicator.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn--indicator");
    if (!btn) return;

    // Переключаем sigtype на all
    btnsSigtype.querySelector(".active").classList.remove("active");
    btnsSigtype.querySelector("[data-sigt='all']").classList.add("active");

    btn.parentElement.querySelector(".active")?.classList.remove("active");
    btn.classList.add("active");

    setState({ indicator: btn.dataset.ind, sigtype: "all" });
    renderTable();
  });
}
