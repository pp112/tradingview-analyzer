// ─── Переключатель типа сигнала ───────────────────────────────────────────

import { setState } from "../state.js";
import { renderTable } from "../table.js";

export function initSigtype() {
  const btns = document.getElementById("sigtypeButtons");

  btns.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn--sigtype");
    if (!btn) return;

    document.querySelectorAll(".btn--sigtype").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    const sigtype          = btn.dataset.sigt;
    const indicatorButtons = document.getElementById("indicatorButtons");
    const topNGroup        = document.getElementById("topNGroup");

    setState({ sigtype });

    // Сброс активного индикатора
    indicatorButtons.querySelector(".active")?.classList.remove("active");

    if (sigtype === "all") {
      topNGroup.style.display = "none";
      indicatorButtons.querySelector("[data-ind='RSI']").classList.add("active");
      setState({ indicator: "RSI" });
    } else {
      topNGroup.style.display = sigtype === "strong" ? "" : "none";
    }

    renderTable();
  });
}
