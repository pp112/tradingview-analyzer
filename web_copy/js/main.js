// ─── Точка входа ──────────────────────────────────────────────────────────

import { initControls } from "./controls.js";
import { bindSorting  } from "./sorting.js";
import { renderTable  } from "./table.js";
// import { connectSSE } from "./api.js"; // раскомментировать при подключении сервера

document.addEventListener("DOMContentLoaded", () => {
  initControls();
  bindSorting();
  renderTable();
  // connectSSE();
});
