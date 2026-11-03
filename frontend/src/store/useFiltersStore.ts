import { create } from "zustand";
import type {
  Timeframe,
  IndicatorType,
  Sigtype,
  SortState,
  SortColumn,
} from "../types/signal";


interface FiltersState {
  timeframe: Timeframe;
  indicator: IndicatorType | null;
  sigtype: Sigtype;
  correlation: number;
  topN: number | null;
  sort: SortState;

  setTimeframe: (tf: Timeframe) => void;
  setIndicator: (ind: IndicatorType) => void;
  setSigtype: (sigtype: Sigtype) => void;
  setCorrelation: (value: number) => void;
  setTopN: (value: number | null) => void;
  toggleSort: (column: SortColumn) => void;
}

export const useFiltersStore = create<FiltersState>((set, get) => ({
  timeframe: "1h",
  indicator: "rsi",
  sigtype: "all",
  correlation: 1,
  topN: null,
  sort: { column: null, direction: 0 },

  setTimeframe: (tf) => set({ timeframe: tf }),

  setIndicator: (ind) => set({ indicator: ind, sigtype: "all" }),

  setSigtype: (sigtype) =>
    set({
      sigtype,
      indicator: sigtype === "all" ? "rsi" : null,
      sort: { column: null, direction: 0 },
    }),

  setCorrelation: (value) => {
    const clamped = Math.max(-1, Math.min(1, value));
    set({ correlation: clamped });
  },

  setTopN: (value) => {
    if (value === null) {
      set({ topN: null });
      return;
    }
    const clamped = Math.max(1, value);
    set({ topN: clamped });
  },

  toggleSort: (column) => {
    const { sort } = get();

    if (sort.column === column) {
      const nextDirection = sort.direction + 1;
      set(
        nextDirection > 2
          ? { sort: { column: null, direction: 0 } }
          : { sort: { column, direction: nextDirection as 1 | 2 } },
      );
    } else {
      set({ sort: { column, direction: 1 } });
    }
  },
}));
