import { useFiltersStore } from "../../store/useFiltersStore";
import type { IndicatorType } from "../../types/signal";

const INDICATORS: { value: IndicatorType; label: string }[] = [
  { value: "rsi", label: "RSI" },
  { value: "macd", label: "MACD" },
  { value: "ema_sma", label: "EMA-SMA" },
  { value: "vol_ratio", label: "VOLUME" },
];

export function IndicatorSwitch() {
  const indicator = useFiltersStore((s) => s.indicator);
  const setIndicator = useFiltersStore((s) => s.setIndicator);

  return (
    <div className="control-group control-group--indicators">
      <span className="control-label">Индикаторы</span>
      <div className="control-buttons">
        {INDICATORS.map((ind) => (
          <button
            key={ind.value}
            className={`btn btn--indicator ${indicator === ind.value ? "active" : ""}`}
            onClick={() => setIndicator(ind.value)}
          >
            {ind.label}
          </button>
        ))}
      </div>
    </div>
  );
}
