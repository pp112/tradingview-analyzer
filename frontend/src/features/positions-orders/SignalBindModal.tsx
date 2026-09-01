import { useMemo, useState } from "react";
import { useSignalsStore } from "../../store/useSignalsStore";
import type { Direction, Signal } from "../../types/signal";
import type { CloseConditionInput, CloseOperator } from "../../types/signalLinks";
import { linkSignalToOrder, linkSignalToPosition } from "../../api/signalLinks";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";

type EntityType = "position" | "order";

type SignalBindModalProps = {
  symbol: string;
  entityType: EntityType;
  orderId?: string;
  direction: Direction;
  onClose: () => void;
};

export function SignalBindModal({ 
  symbol, 
  entityType, 
  orderId, 
  direction, 
  onClose 
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
    const result: Signal[] = [];
    for (const list of Object.values(allSignals)) {
      if (!list) continue;
      result.push(
        ...list.filter((s) => s.symbol === symbol && s.direction === direction)
      );
    }
    return result;
  }, [allSignals, symbol, direction]);

  const selected = selectedIndex !== null ? availableSignals[selectedIndex] : null;

  const handleConfirm = async () => {
    if (!selected) return;

    let closeCondition: CloseConditionInput | null = null;

    if (withCloseCondition) {
      const parsed = parseFloat(targetValue.replace(",", "."));
      if (isNaN(parsed)) {
        setError("Введите корректное числовое значение для условия закрытия");
        return;
      }
      closeCondition = { operator: closeOperator, target_value: parsed }
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
            value: selected.indicator === "vol_ratio"
              ? selected.vol_ratio
              : selected.indicator_value,
            direction: selected.direction,
          },
          close_condition: closeCondition,
        });
        addPositionLink(link);
      } else {
        if (!orderId) return;
        const link = await linkSignalToOrder({
          symbol,
          order_id: orderId,
          signal: {
            indicator: selected.indicator,
            timeframe: selected.timeframe,
            value: selected.indicator === "vol_ratio"
              ? selected.vol_ratio
              : selected.indicator_value,
            direction: selected.direction,
          },
          close_condition: closeCondition,
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
          <button className="po-icon-btn" onClick={onClose}>
            ×
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
                  {s.indicator_value} · {s.direction}
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
              <div className="po-close-condition">
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

        {error && <p className="po-error-text">{error}</p>}

        <div className="po-modal-actions">
          <button className="po-secondary-btn" onClick={onClose}>
            Отмена
          </button>
          <button 
            className="po-primary-btn" 
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
