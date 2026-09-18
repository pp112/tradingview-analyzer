import type { Direction, IndicatorType, Timeframe } from "./signal";

export type CloseOperator = ">=" | "<=";

export type SignalSnapshotInput = {
  indicator: IndicatorType;
  timeframe: Timeframe;
  value: number;
  direction: Direction;
};

export type CloseConditionInput = {
  operator: CloseOperator;
  targetValue: number;
};

export type LinkPositionSignalRequest = {
  symbol: string;
  signal: SignalSnapshotInput;
  closeCondition: CloseConditionInput | null;
};

export type LinkOrderSignalRequest = {
  symbol: string;
  exchangeOrderId: string;
  signal: SignalSnapshotInput;
  closeCondition: CloseConditionInput | null;
};

export type SignalSnapshotResponse = {
  id: number;
  indicator: IndicatorType;
  timeframe: Timeframe;
  value: number;
  direction: Direction;
};

export type CloseConditionResponse = {
  id: number;
  operator: CloseOperator;
  targetValue: number;
};

export type PositionSignalLinkResponse = {
  id: number;
  symbol: string;
  signal: SignalSnapshotResponse;
  closeCondition: CloseConditionResponse;
  createdAt: string;
};

export type OrderSignalLinkResponse = {
  id: number;
  symbol: string;
  exchangeOrderId: string;
  signal: SignalSnapshotResponse;
  closeCondition: CloseConditionResponse;
  createdAt: string;
};

export type CurrentIndicatorValue = {
  symbol: string;
  indicator: IndicatorType;
  value: number;
};
