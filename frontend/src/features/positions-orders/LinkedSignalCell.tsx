import { useEffect, useState } from "react";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import type { IndicatorType } from "../../types/signal";
import type {
  OrderSignalLinkResponse,
  PositionSignalLinkResponse,
} from "../../types/signalLinks";
import { X } from "lucide-react";

type LinkType = PositionSignalLinkResponse | OrderSignalLinkResponse;

type LinkedSignalCellProps = {
  link: LinkType | undefined;
  onBindClick: () => void;
  onUnbindClick: () => void;
};

const INDICATOR_LABELS: Record<IndicatorType, string> = {
  rsi: "rsi",
  macd: "macd",
  ema_sma: "ema-sma",
  vol_ratio: "volume",
};

const getIndicatorDisplayName = (indicator: IndicatorType): string =>
  INDICATOR_LABELS[indicator].toUpperCase().replace("-", "+");

function formatTimeAgo(isoString: string, now: number): string {
  const date = new Date(isoString);
  const minutes = Math.floor((now - date.getTime()) / 60_000);
  if (minutes < 1) return "только что";
  if (minutes < 60) return `${minutes} мин назад`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} ч назад`;
  const days = Math.floor(hours / 24);
  return `${days} дн назад`
}

export function LinkedSignalCell({
  link,
  onBindClick,
  onUnbindClick,
}: LinkedSignalCellProps) {
  const getCurrentValue = useSignalLinksStore((s) => s.getCurrentValue);

  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const interval = setInterval(() => {
      setNow(Date.now());
    }, 60_000);

    return () => clearInterval(interval);
  }, []);

  if (!link) {
    return (
      <button className="po-action-btn" onClick={onBindClick}>
        + Привязать сигнал
      </button>
    );
  }

  const fixedValue = link.signal.value;
  const currentValue = getCurrentValue(
    link.symbol,
    link.signal.indicator,
    link.signal.timeframe,
  );

  const difference = currentValue !== null ? currentValue - fixedValue : 0;
  const differenceClass = difference >= 0 ? "pos" : "neg";

  return (
    <div className="po-signal">
      <div className="po-signal-head">
        <span
          className={`po-indicator ${INDICATOR_LABELS[link.signal.indicator]}`}
        >
          {getIndicatorDisplayName(link.signal.indicator)}
        </span>
        <span className="po-timeframe">
          {link.signal.timeframe.toUpperCase()}
        </span>
        <span className="po-age ">
          {formatTimeAgo(link.created_at, now)}
        </span>
        <button
          className="po-icon-btn unlink"
          onClick={onUnbindClick}
          title="Отвязать сигнал"
        >
          <X size={12} strokeWidth={2.5} />
        </button>
      </div>

      <div className="po-signal-values">
        <span className="indicator">
          {getIndicatorDisplayName(link.signal.indicator)}:
        </span>
        <span className="value">{fixedValue}</span>
        <span className="arrow">→</span>
        <span className="value">{currentValue ?? fixedValue}</span>
        <span className={differenceClass}>
          ({difference >= 0 ? "+" : ""}
          {difference.toFixed(2)})
        </span>
      </div>
    </div>
  );
}