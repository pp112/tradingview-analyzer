import { useFiltersStore } from "../../../store/useFiltersStore";
import type { Timeframe } from "../../../types/signal";

const TIMEFRAMES: Timeframe[] = ["15m", "30m", "1h", "4h", "1d"];

export function TimeframeSwitch() {
  const timeframe = useFiltersStore((s) => s.timeframe);
  const setTimeframe = useFiltersStore((s) => s.setTimeframe);

  return (
    <div className="control-group control-group--timeframe">
      <span className="control-label">Таймфрейм</span>
      <div className="control-buttons">
        {TIMEFRAMES.map((tf) => (
          <button
            key={tf}
            className={`btn btn--tf ${timeframe === tf ? "active" : ""}`}
            onClick={() => setTimeframe(tf)}
          >
            {tf.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
