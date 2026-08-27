import type { ActionResponse } from "../types/api";
import { apiDelete, apiGet, apiPost } from "./client";
import type { 
  LinkOrderSignalRequest, 
  LinkPositionSignalRequest, 
  OrderSignalLinkResponse, 
  PositionSignalLinkResponse,
} from "../types/signalLinks";

export async function fetchPositionLinks(): Promise<PositionSignalLinkResponse[]> {
  return apiGet<PositionSignalLinkResponse[]>("/links/positions");
}

export async function linkSignalToPosition(
  data: LinkPositionSignalRequest
): Promise<PositionSignalLinkResponse> {
  return apiPost<PositionSignalLinkResponse>("/links/positions", data)
}

export async function unlinkSignalFromPosition(link_id: number): Promise<ActionResponse> {
  return apiDelete<ActionResponse>(`/links/positions/${link_id}`);
}

export async function fetchOrderLinks(): Promise<OrderSignalLinkResponse[]> {
  return apiGet<OrderSignalLinkResponse[]>("/links/orders");
}

export async function linkSignalToOrder(
  data: LinkOrderSignalRequest
): Promise<OrderSignalLinkResponse> {
  return apiPost<OrderSignalLinkResponse>("/links/orders", data)
}

export async function unlinkSignalFromOrder(link_id: number): Promise<ActionResponse> {
  return apiDelete<ActionResponse>(`/links/orders/${link_id}`);
}