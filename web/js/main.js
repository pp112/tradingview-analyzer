// ─── Точка входа ──────────────────────────────────────────────────────────

import { initControls } from "./controls.js";
import { renderTable  } from "./table.js";
import { connectSSE } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  initControls();
  renderTable();
  connectSSE();
});
