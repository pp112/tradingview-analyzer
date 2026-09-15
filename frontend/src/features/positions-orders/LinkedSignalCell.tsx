import { useEffect, useRef, useState } from "react";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import { formatTimeAgo } from "../../utils/formatTimeAgo";
import type { IndicatorType } from "../../types/signal";
import type {
  OrderSignalLinkResponse,
  PositionSignalLinkResponse,
} from "../../types/signalLinks";
import { MoveRight, X } from "lucide-react";
import { ConfirmPopover } from "../../components/ui/ConfirmPopover";

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


export function LinkedSignalCell({
  link,
  onBindClick,
  onUnbindClick,
}: LinkedSignalCellProps) {
  const getCurrentValue = useSignalLinksStore((s) => s.getCurrentValue);

  const [now, setNow] = useState(() => Date.now());
  const [confirmUnbind, setConfirmUnbind] = useState(false);
  
  const unbindBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setNow(Date.now());
    }, 60_000);

    return () => clearInterval(interval);
  }, []);

  if (!link) {
    return (
      <button className="po-btn bind" onClick={onBindClick}>
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
          ref={unbindBtnRef}
          className="po-btn unbind"
          onClick={() => setConfirmUnbind((prev) => !prev)}
          title="Отвязать сигнал"
        >
          <X size={12} strokeWidth={2.5} />
        </button>
        {confirmUnbind && (
          <ConfirmPopover
            anchorRef={unbindBtnRef}
            message="Отвязать сигнал?"
            onConfirm={() => {
              setConfirmUnbind(false);
              onUnbindClick();
            }}
            onCancel={() => setConfirmUnbind(false)}
          />
        )}
      </div>

      <div className="po-signal-values">
        <span className="indicator">
          {getIndicatorDisplayName(link.signal.indicator)}:
        </span>
        <span className="value">{fixedValue}</span>
        <MoveRight className="arrow" size={15} />
        <span className="value">{currentValue ?? fixedValue}</span>
        <span className={differenceClass}>
          ({difference >= 0 ? "+" : ""}
          {difference.toFixed(2)})
        </span>
      </div>
    </div>
  );
}