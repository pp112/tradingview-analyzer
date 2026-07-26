import { create } from "zustand";
import type { PriceVolumeData } from "../types/priceVolume";
import type { Signal, Timeframe } from "../types/signal";

interface SignalsState {
  signals: Partial<Record<Timeframe, Signal[]>>;
  priceVolume: PriceVolumeData | null;

  setSignals: (timeframe: Timeframe, data: Signal[]) => void;
  setAllSignals: (signals: Partial<Record<Timeframe, Signal[]>>) => void;
  setPriceVolume: (data: PriceVolumeData) => void;
}

export const useSignalsStore = create<SignalsState>((set) => ({
  signals: {},
  priceVolume: null,

  setSignals: (timeframe, data) =>
    set((state) => ({
      signals: { ...state.signals, [timeframe]: data },
    })),

  setAllSignals: (signalsByTf) => set({ signals: signalsByTf }),

  setPriceVolume: (data) => set({ priceVolume: data }),
}));
