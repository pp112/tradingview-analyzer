import { create } from "zustand";
import type { OrderSignalLinkResponse, PositionSignalLinkResponse } from "../types/signalLinks";

interface SignalLinksState {
  positionLinks: PositionSignalLinkResponse[];
  orderLinks: OrderSignalLinkResponse[];

  setPositionLinks: (links: PositionSignalLinkResponse[]) => void;
  setOrderLinks: (links: OrderSignalLinkResponse[]) => void;

  addPositionLink: (link: PositionSignalLinkResponse) => void;
  addOrderLink: (link: OrderSignalLinkResponse) => void;

  removePositionLink: (linkId: number) => void;
  removeOrderLink: (linkId: number) => void;
}

export const useSignalLinksStore = create<SignalLinksState>((set) => ({
  positionLinks: [],
  orderLinks: [],

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
}))