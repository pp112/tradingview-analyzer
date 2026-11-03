import type { CombinedSignal, Signal, SortState } from "../types/signal";
import { getSignalValue } from "./signal";

export function filterStrong(rows: Signal[], topN: number | null): Signal[] {
  const byIndicator = (indicator: Signal["indicator"]) => {
    const sorted = rows
      .filter((row) => row.indicator === indicator)
      .sort((a, b) => getSignalValue(b) - getSignalValue(a));

    return topN === null ? sorted : sorted.slice(0, topN);
  };

  return [
    ...byIndicator("rsi"),
    ...byIndicator("macd"),
    ...byIndicator("emaSma"),
  ];
}

export function filterCombined(rows: Signal[]): CombinedSignal[] {
  const countBySymbol: Record<string, number> = {};
  rows.forEach((row) => {
    countBySymbol[row.symbol] = (countBySymbol[row.symbol] || 0) + 1;
  });

  const combined = rows.filter((row) => countBySymbol[row.symbol] >= 2);

  const grouped: Record<string, CombinedSignal> = {};
  combined.forEach((row) => {
    if (!grouped[row.symbol]) {
      grouped[row.symbol] = {
        symbol: row.symbol,
        direction: row.direction,
        rsi: null,
        macd: null,
        emaSma: null,
        volRatio: row.volRatio,
        correlation: row.correlation,
      };
    }
    grouped[row.symbol][row.indicator] = getSignalValue(row);
  });

  return Object.values(grouped).filter((group) => {
    const symbolRows = combined.filter((row) => row.symbol === group.symbol);
    const directions = new Set(symbolRows.map((row) => row.direction));
    return directions.size === 1;
  });
}

export function sortByColumn<T extends Record<string, unknown>>(
  rows: T[],
  sort: SortState,
): T[] {
  const { column, direction } = sort;
  if (!column || direction === 0) return rows;

  const order = direction === 1 ? -1 : 1;
  const sortedRows = [...rows];

  const getSortValue = (row: T) =>
    column === "signalValue" && "indicator" in row
      ? getSignalValue(row as unknown as Signal)
      : row[column];

  sortedRows.sort((a, b) => {
    const v1 = getSortValue(a);
    const v2 = getSortValue(b);

    if (v1 === null) return 1;
    if (v2 === null) return -1;

    if (typeof v1 === "string" && typeof v2 === "string") {
      return v1.localeCompare(v2) * order;
    }

    return ((v1 as number) - (v2 as number)) * order;
  });

  return sortedRows;
}

export function applyTopN<T>(rows: T[], topN: number | null): T[] {
  return topN === null ? rows : rows.slice(0, topN);
}
