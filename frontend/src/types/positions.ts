export type Side = "long" | "short";

export type Order = {
  id: string;
  symbol: string;
  side: Side;
};

export type Position = {
  symbol: string;
  side: Side;
  pnl: number;
  pnlPct: number;
};

export type BalanceResponse = {
  balance: number | null;
};
