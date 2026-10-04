import { useEffect, useRef, useState } from "react";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import { formatTimeAgo } from "../../utils/formatTimeAgo";
import type { IndicatorType } from "../../types/signal";
import type {
  OrderSignalLinkResponse,
  PositionSignalLinkResponse,
} from "../../types/signalLinks";
import { Link, MoveRight, PenLine, X } from "lucide-react";
import { ConfirmPopover } from "../../components/ui/ConfirmPopover";

type LinkType = PositionSignalLinkResponse | OrderSignalLinkResponse;

type LinkedSignalCellProps = {
  link: LinkType | undefined;
  onBindClick: () => void;
  onEditClick: () => void;
  onUnbindClick: () => void;
};

const INDICATOR_LABELS: Record<IndicatorType, string> = {
  rsi: "rsi",
  macd: "macd",
  emaSma: "emasma",
  volRatio: "volume",
};

const getIndicatorDisplayName = (indicator: IndicatorType): string =>
  INDICATOR_LABELS[indicator].toUpperCase();

export function LinkedSignalCell({
  link,
  onBindClick,
  onEditClick,
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
        <Link size={13} strokeWidth={2.5} />
        Привязать сигнал
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
          className={`po-signal-indicator ${INDICATOR_LABELS[link.signal.indicator]}`}
        >
          {getIndicatorDisplayName(link.signal.indicator)}
        </span>
        <span className="po-signal-timeframe">
          {link.signal.timeframe.toUpperCase()}
        </span>
        <span className="po-signal-age">
          {formatTimeAgo(link.createdAt, now)}
        </span>
        <div className="po-signal-actions">
          <button
            className="po-btn edit"
            onClick={onEditClick}
            title="Изменить сигнал"
          >
            <PenLine size={11} strokeWidth={2.5} />
          </button>
          <button
            ref={unbindBtnRef}
            className="po-btn unbind"
            onClick={() => setConfirmUnbind((prev) => !prev)}
            title="Отвязать сигнал"
          >
            <X size={13} strokeWidth={2.5} />
          </button>
        </div>
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
