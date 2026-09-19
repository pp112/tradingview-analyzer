import { useMemo, useState } from "react";
import { useSignalsStore } from "../../store/useSignalsStore";
import type { Direction, Signal, Timeframe } from "../../types/signal";
import type {
  CloseConditionInput,
  CloseOperator,
} from "../../types/signalLinks";
import { linkSignalToOrder, linkSignalToPosition } from "../../api/signalLinks";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import { X } from "lucide-react";

type EntityType = "position" | "order";

type SignalBindModalProps = {
  symbol: string;
  entityType: EntityType;
  exchangeOrderId?: string;
  direction: Direction;
  onClose: () => void;
};

type AvailableSignals = Signal & {
  timeframe: Timeframe;
};

export function SignalBindModal({
  symbol,
  entityType,
  exchangeOrderId,
  direction,
  onClose,
}: SignalBindModalProps) {
  const allSignals = useSignalsStore((s) => s.signals);
  const addPositionLink = useSignalLinksStore((s) => s.addPositionLink);
  const addOrderLink = useSignalLinksStore((s) => s.addOrderLink);

  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [withCloseCondition, setWithCloseCondition] = useState(false);
  const [closeOperator, setCloseOperator] = useState<CloseOperator>("<=");
  const [targetValue, setTargetValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const availableSignals = useMemo(() => {
    const result: AvailableSignals[] = [];
    for (const [timeframe, list] of Object.entries(allSignals)) {
      if (!list) continue;
      result.push(
        ...list
          // .filter((s) => s.symbol === symbol && s.direction === direction)
          .filter((s) => s.symbol !== "qwe")
          .map((signal) => ({
            ...signal,
            timeframe: timeframe as Timeframe,
          })),
      );
    }
    return result;
  }, [allSignals, symbol, direction]);

  const selected =
    selectedIndex !== null ? availableSignals[selectedIndex] : null;

  const handleConfirm = async () => {
    if (!selected) return;

    let closeCondition: CloseConditionInput | null = null;

    if (withCloseCondition) {
      const parsed = parseFloat(targetValue.replace(",", "."));
      if (isNaN(parsed)) {
        setError("Введите корректное числовое значение для условия закрытия");
        return;
      }
      closeCondition = { operator: closeOperator, targetValue: parsed };
    }

    setLoading(true);
    setError(null);

    try {
      if (entityType === "position") {
        const link = await linkSignalToPosition({
          symbol,
          signal: {
            indicator: selected.indicator,
            timeframe: selected.timeframe,
            value:
              selected.indicator === "volRatio"
                ? selected.volRatio
                : selected.indicatorValue,
            direction: selected.direction,
          },
          closeCondition: closeCondition,
        });
        addPositionLink(link);
      } else {
        if (!exchangeOrderId) return;
        const link = await linkSignalToOrder({
          symbol,
          exchangeOrderId: exchangeOrderId,
          signal: {
            indicator: selected.indicator,
            timeframe: selected.timeframe,
            value:
              selected.indicator === "volRatio"
                ? selected.volRatio
                : selected.indicatorValue,
            direction: selected.direction,
          },
          closeCondition: closeCondition,
        });
        addOrderLink(link);
      }
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error && err.message.includes("409")) {
        setError("Сигнал уже привязан к этой позиции/ордеру");
      } else {
        setError("Не удалось привязать сигнал. Попробуйте ещё раз.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="po-modal">
      <div className="po-modal-backdrop" onClick={onClose} />
      <div className="po-modal-dialog" role="dialog" aria-modal="true">
        <div className="po-modal-header">
          <div>
            <h3>Привязать сигнал</h3>
            <p>{symbol}</p>
          </div>
          <button className="po-btn close" onClick={onClose}>
            <X size={14} strokeWidth={2.5} />
          </button>
        </div>

        {availableSignals.length === 0 ? (
          <p className="po-empty">Нет доступных сигналов по этому символу</p>
        ) : (
          <>
            <label className="po-field-label" htmlFor="poSignalSelect">
              Сигнал
            </label>
            <select
              className="po-select"
              id="poSignalSelect"
              value={selectedIndex ?? ""}
              onChange={(e) => {
                const val = e.target.value;
                setSelectedIndex(val === "" ? null : Number(val));
              }}
            >
              <option value="" disabled>
                Выбрать сигнал
              </option>
              {availableSignals.map((s, i) => (
                <option key={`${s.indicator}-${s.timeframe}-${i}`} value={i}>
                  {s.indicator.toUpperCase()} · {s.timeframe} ·{" "}
                  {s.indicatorValue.toFixed(2)} · {s.direction}
                </option>
              ))}
            </select>

            <div className="po-checkbox">
              <label className="po-field-label po-checkbox-label">
                <input
                  type="checkbox"
                  checked={withCloseCondition}
                  onChange={(e) => setWithCloseCondition(e.target.checked)}
                />
                Включить автозакрытие
              </label>
            </div>

            {withCloseCondition && (
              <div className="po-modal-close-condition">
                <select
                  className="po-select"
                  style={{ width: 90 }}
                  value={closeOperator}
                  onChange={(e) =>
                    setCloseOperator(e.target.value as CloseOperator)
                  }
                >
                  <option value="<=">Меньше</option>
                  <option value=">=">Больше</option>
                </select>
                <input
                  className="po-select"
                  type="text"
                  placeholder="Значение"
                  value={targetValue}
                  onChange={(e) => setTargetValue(e.target.value)}
                />
              </div>
            )}
          </>
        )}

        {error && <p className="po-modal-error-text">{error}</p>}

        <div className="po-modal-actions">
          <button className="po-btn secondary" onClick={onClose}>
            Отмена
          </button>
          <button
            className="po-btn primary"
            onClick={handleConfirm}
            disabled={!selected || loading}
          >
            {loading ? "Привязка..." : "Привязать сигнал"}
          </button>
        </div>
      </div>
    </div>
  );
}
