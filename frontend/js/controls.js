// ─── Инициализация всех элементов управления ─────────────────────────────

import { initTimeframe   } from "./controls/timeframe.js";
import { initIndicator   } from "./controls/indicator.js";
import { initSigtype     } from "./controls/sigtype.js";
import { initCorrelation } from "./controls/correlation.js";
import { initTopN        } from "./controls/topn.js";
import { initSort        } from "./controls/sort.js";

export function initControls() {
  initTimeframe();
  initIndicator();
  initSigtype();
  initCorrelation();
  initTopN();
  initSort();
}
