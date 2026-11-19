import { create } from "zustand";
import type { Order, PortfolioResponse, Position } from "../types/portfolio";

interface PortfolioState {
  positions: Position[];
  orders: Order[];
  balance: number | null;
  updatedAt: number | null;

  setPortfolio: (portfolio: PortfolioResponse) => void;
  removeOrder: (exchangeOrderId: string) => void;
  removePosition: (symbol: string) => void;
}

export const usePortfolioStore = create<PortfolioState>((set) => ({
  positions: [],
  orders: [],
  balance: null,
  updatedAt: null,
  
  setPortfolio: (portfolio) =>
    set({
      positions: [...portfolio.positions].sort((a, b) => a.createdAt - b.createdAt),
      orders: [...portfolio.orders].sort((a, b) => a.createdAt - b.createdAt),
      balance: portfolio.balance,
      updatedAt: portfolio.updatedAt,
    }),

  removeOrder: (exchangeOrderId) =>
    set((state) => ({
      orders: state.orders.filter((o) => o.exchangeOrderId !== exchangeOrderId),
    })),
  removePosition: (symbol) =>
    set((state) => ({
      positions: state.positions.filter((p) => p.symbol !== symbol),
    })),
}));
