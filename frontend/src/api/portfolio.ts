import type { PortfolioResponse } from "../types/portfolio";
import type { ActionResponse } from "../types/api";
import { apiGet, apiPost } from "./client";

export async function fetchPortfolio(): Promise<PortfolioResponse> {
  return apiGet<PortfolioResponse>("/portfolio");
}

export async function cancelOrder(
  exchangeOrderId: string,
): Promise<ActionResponse> {
  return apiPost<ActionResponse>(`/orders/${exchangeOrderId}/cancel`);
}

export async function closePosition(symbol: string): Promise<ActionResponse> {
  return apiPost<ActionResponse>(
    `/positions/close?symbol=${encodeURIComponent(symbol)}`,
  );
}
