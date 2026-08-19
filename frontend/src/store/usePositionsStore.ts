import { create } from "zustand";
import type { Order, Position } from "../types/positions";

type LoadStatus = "idle" | "loading" | "loaded" | "error";

interface PositionsState {
  positions: Position[];
  orders: Order[];
  balance: number | null;
  status: LoadStatus;

  setPositions: (positions: Position[]) => void;
  setOrders: (orders: Order[]) => void;
  setBalance: (balance: number | null) => void;
  setStatus: (status: LoadStatus) => void;
  removeOrder: (orderId: string) => void;
  removePosition: (symbol: string) => void;
}

export const usePositionsStore = create<PositionsState>((set) => ({
  positions: [],
  orders: [],
  balance: null,
  status: "idle",

  setPositions: (positions) => set({ positions }),
  setOrders: (orders) => set({ orders }),
  setBalance: (balance) => set({ balance }),
  setStatus: (status) => set({ status }),

  removeOrder: (orderId) =>
    set((state) => ({
      orders: state.orders.filter((o) => o.id !== orderId),
    })),
  removePosition: (symbol) =>
    set((state) => ({
      positions: state.positions.filter((p) => p.symbol !== symbol),
    })),
}));
