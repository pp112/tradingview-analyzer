import type { IndicatorType } from "../../types/signal";
import type { OrderSignalLinkResponse, PositionSignalLinkResponse } from "../../types/signalLinks";

type LinkType = PositionSignalLinkResponse | OrderSignalLinkResponse;

type LinkedSignalCellProps = {
  link: LinkType | undefined;
}

const INDICATOR_LABELS: Record<IndicatorType, string> = {
  rsi: "rsi",
  macd: "macd",
  ema_sma: "ema-sma",
  vol_ratio: "volume",
};

const getIndicatorDisplayName = (indicator: IndicatorType): string =>
  INDICATOR_LABELS[indicator].toUpperCase().replace("-", "+");


export function LinkedSignalCell({ link }: LinkedSignalCellProps) {
  if (!link) {
    return (
      <button className="po-action-btn" onClick={onBindClick}>
        + Привязать сигнал
      </button>
    );
  }

  const fixedValue = link.signal.value;
  const currentValue = 0.12;

  const difference = currentValue - fixedValue;
  const differenceClass = difference > 0 ? "pos" : difference < 0 ? "neg" : "value";

  return (
    <div className="po-signal">
      <div className="po-signal-head">
        <span className={`po-indicator ${INDICATOR_LABELS[link.signal.indicator]}`}>
          {getIndicatorDisplayName(link.signal.indicator)}
        </span>
        <span className="po-timeframe">{link.signal.timeframe.toUpperCase()}</span>
        <button
          className="po-icon-btn unlink"
          // onClick={onUnbindClick}
          title="Отвязать сигнал"
          >
            ×
        </button>
      </div>

      <div className="po-signal-values">
        <span className="indicator">{getIndicatorDisplayName(link.signal.indicator)}:</span>
        <span className="value">{fixedValue}</span>
        <span className="arrow">→</span>
        <span className="value">
          {currentValue !== null ? currentValue : "—"}
        </span>
        (<span className={differenceClass}>{difference > 0 ? "+" : ""}{difference}</span>)
      </div>
    </div>
  );
}