import type { BalanceResponse, Order, Position } from "../types/positions";
import type { ActionResponse } from "../types/api";
import { apiGet, apiPost } from "./client";

export async function fetchPositions(): Promise<Position[]> {
  return apiGet<Position[]>("/positions");
}

export async function fetchOrders(): Promise<Order[]> {
  return apiGet<Order[]>("/orders");
}

export async function fetchBalance(): Promise<BalanceResponse> {
  return apiGet<BalanceResponse>("/balance");
}

export async function cancelOrder(orderId: string): Promise<ActionResponse> {
  return apiPost<ActionResponse>(`/orders/${orderId}/cancel`);
}

export async function closePosition(symbol: string): Promise<ActionResponse> {
  return apiPost<ActionResponse>(`/positions/${symbol}/close`);
}
