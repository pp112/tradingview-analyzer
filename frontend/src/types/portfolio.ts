export type Side = "long" | "short";

export type Order = {
  exchangeOrderId: string;
  symbol: string;
  side: Side;
  createdAt: number;
};

export type Position = {
  symbol: string;
  side: Side;
  pnl: number;
  pnlPct: number | null;
  createdAt: number;
};

export type PortfolioResponse = {
  positions: Position[];
  orders: Order[];
  balance: number | null;
  updatedAt: number | null;
};
