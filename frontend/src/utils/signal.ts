import type { Signal } from "../types/signal";

export function getSignalValue(signal: Signal): number {
  return "value" in signal ? signal.value : signal.strength;
}