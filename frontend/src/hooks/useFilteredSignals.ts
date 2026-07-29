import { useMemo } from "react";
import { useFiltersStore } from "../store/useFiltersStore";
import { useSignalsStore } from "../store/useSignalsStore";
import type { CombinedSignal, Signal } from "../types/signal";
import { applyTopN, filterCombined, filterStrong, sortByColumn } from "../utils/sorting";

export function useFilteredSignals(): Signal[] | CombinedSignal[] {
  const timefrarme = useFiltersStore((s) => s.timeframe);
  const indicator = useFiltersStore((s) => s.indicator);
  const sigtype = useFiltersStore((s) => s.sigtype);
  const correlation = useFiltersStore((s) => s.correlation);
  const topN = useFiltersStore((s) => s.topN);
  const sort = useFiltersStore((s) => s.sort);

  const signals = useSignalsStore((s) => s.signals[timefrarme] ?? []);

  return useMemo(() => {
    let rows: Signal[] = signals;

    if (sigtype == "all" && indicator !== null) {
      rows = rows.filter((s) => s.indicator === indicator);
    }

    rows = rows.filter((s) => s.correlation <= correlation);

    if (sigtype === "combined") {
      const filtered = filterCombined(rows);
      return sortByColumn(filtered, sort);
    } 

    const filtered = sigtype === "strong" ? filterStrong(rows, topN) : rows;
    let result = sortByColumn(filtered, sort);

    if (sigtype !== "strong") {
      result = applyTopN(result, topN);
    }

    return result;
  }, [signals, indicator, sigtype, correlation, topN, sort]);
}
