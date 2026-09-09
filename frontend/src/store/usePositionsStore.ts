import { create } from "zustand";
import type { Order, Position } from "../types/positions";

interface PositionsState {
  positions: Position[];
  orders: Order[];
  balance: number | null;
  updatedAt: number | null;

  setPositions: (positions: Position[]) => void;
  setOrders: (orders: Order[]) => void;
  setBalance: (balance: number | null) => void;
  setUpdatedAt: (updateAt: number) => void;
  removeOrder: (orderId: string) => void;
  removePosition: (symbol: string) => void;
}

export const usePositionsStore = create<PositionsState>((set) => ({
  positions: [],
  orders: [],
  balance: null,
  updatedAt: null,
  status: "idle",

  setPositions: (positions) => set({ positions }),
  setOrders: (orders) => set({ orders }),
  setBalance: (balance) => set({ balance }),
  setUpdatedAt: (updatedAt) => set({ updatedAt }),

  removeOrder: (orderId) =>
    set((state) => ({
      orders: state.orders.filter((o) => o.id !== orderId),
    })),
  removePosition: (symbol) =>
    set((state) => ({
      positions: state.positions.filter((p) => p.symbol !== symbol),
    })),
}));
