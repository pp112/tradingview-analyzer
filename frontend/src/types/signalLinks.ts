import type { Direction, IndicatorType, Timeframe } from "./signal";

type CloseOperator = ">=" | "<=";

type SignalSnapshotInput = {
  indicator: IndicatorType;
  timeframe: Timeframe;
  value: number;
  direction: Direction;
};

type CloseConditionInput = {
  operator: CloseOperator;
  target_value: number;
};

export type LinkPositionSignalRequest = {
  symbol: string;
  signal: SignalSnapshotInput;
  close_condition: CloseConditionInput | null;
};

export type LinkOrderSignalRequest = {
  symbol: string;
  order_id: string;
  signal: SignalSnapshotInput;
  close_condition: CloseConditionInput | null;
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
  target_value: number;
};

export type PositionSignalLinkResponse = {
  id: number;
  symbol: string;
  signal: SignalSnapshotResponse;
  close_condition: CloseConditionResponse;
};

export type OrderSignalLinkResponse = {
  id: number;
  symbol: string;
  order_id: string;
  signal: SignalSnapshotResponse;
  close_condition: CloseConditionResponse;
};
