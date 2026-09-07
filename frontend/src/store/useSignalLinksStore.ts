import { create } from "zustand";
import type { CurrentIndicatorValue, OrderSignalLinkResponse, PositionSignalLinkResponse } from "../types/signalLinks";
import type { IndicatorType, Timeframe } from "../types/signal";

function makeValueKey(symbol: string, indicator: IndicatorType, timeframe: Timeframe): string {
  return `${symbol}:${indicator}:${timeframe}`
}

interface SignalLinksState {
  positionLinks: PositionSignalLinkResponse[];
  orderLinks: OrderSignalLinkResponse[];
  currentValues: Record<string, number>;

  setPositionLinks: (links: PositionSignalLinkResponse[]) => void;
  setOrderLinks: (links: OrderSignalLinkResponse[]) => void;

  addPositionLink: (link: PositionSignalLinkResponse) => void;
  addOrderLink: (link: OrderSignalLinkResponse) => void;

  removePositionLink: (linkId: number) => void;
  removeOrderLink: (linkId: number) => void;

  setCurrentValues: (values: CurrentIndicatorValue[], timeframe: Timeframe) => void;
  getCurrentValue: (symbol: string, indicator: IndicatorType, timeframe: Timeframe) => number | null;
}

export const useSignalLinksStore = create<SignalLinksState>((set, get) => ({
  positionLinks: [],
  orderLinks: [],
  currentValues: {},

  setPositionLinks: (links) => set({ positionLinks: links }),
  setOrderLinks: (links) => set({ orderLinks: links }),

  addPositionLink: (link) => 
    set((state) => ({ positionLinks: [...state.positionLinks, link] })),
  addOrderLink: (link) => 
    set((state) => ({ orderLinks: [...state.orderLinks, link] })),

  removePositionLink: (linkId) =>
    set((state) => ({
      positionLinks: state.positionLinks.filter((l) => l.id !== linkId),
    })),
  removeOrderLink: (linkId) =>
    set((state) => ({
      orderLinks: state.orderLinks.filter((l) => l.id !== linkId),
    })),

  setCurrentValues: (values, timeframe) =>
    set((state) => {
      const updated = { ...state.currentValues };
      for (const v of values) {
        updated[makeValueKey(v.symbol, v.indicator, timeframe)] = v.value;
      }
      return { currentValues: updated };
    }),

  getCurrentValue: (symbol, indicator, timeframe) => {
    const key = makeValueKey(symbol, indicator, timeframe);
    return get().currentValues[key] ?? null;
  }
}))