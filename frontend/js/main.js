// ─── Точка входа ──────────────────────────────────────────────────────────

import { initControls } from "./controls.js";
import { connectSSE } from "./api.js";
import { onSignals, onPriceVolume, onInit } from "./handlers.js";


document.addEventListener("DOMContentLoaded", () => {
  initControls();
  onInit();
  connectSSE({ onSignals, onPriceVolume });
});
