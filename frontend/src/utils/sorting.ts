import type { CombinedSignal, Signal, SortState } from "../types/signal";

export function filterStrong(rows: Signal[], topN: number | null): Signal[] {
  const byIndicator = (indicator: Signal["indicator"]) => {
    const sorted = rows
      .filter((row) => row.indicator === indicator)
      .sort((a, b) => b.indicator_value - a.indicator_value);

    return topN === null ? sorted : sorted.slice(0, topN);
  };

  return [
    ...byIndicator("rsi"),
    ...byIndicator("macd"),
    ...byIndicator("ema_sma"),
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
        ema_sma: null,
        vol_ratio: row.vol_ratio,
        correlation: row.correlation,
      };
    }
    grouped[row.symbol][row.indicator] = row.indicator_value;
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

  sortedRows.sort((a, b) => {
    const v1 = a[column];
    const v2 = b[column];

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
