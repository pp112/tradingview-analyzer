import { useMemo, useState } from "react";
import { useSignalsStore } from "../../store/useSignalsStore";
import type { Direction, Signal, Timeframe } from "../../types/signal";
import type {
  CloseConditionInput,
  CloseOperator,
} from "../../types/signalLinks";
import { linkSignalToOrder, linkSignalToPosition } from "../../api/signalLinks";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import { Link, X } from "lucide-react";

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
  const [withCloseCondition, setWithCloseCondition] = useState(true);
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
    <div className="sbm">
      <div className="sbm-backdrop" onClick={onClose} />
      <div className="sbm-dialog" role="dialog" aria-modal="true">
        <div className="sbm-header">
          <div className="sbm-title">
            <span className="sbm-header-icon">
              <Link size={19} strokeWidth={2.2} />
            </span>
            <div className="sbm-header-text">
              <h3>Привязать сигнал</h3>
              <p>{symbol}</p>
            </div>
          </div>
          <button className="po-btn close" onClick={onClose}>
            <X size={14} strokeWidth={2.5} />
          </button>
        </div>

        {/* {availableSignals.length === 0 ? (
          <p className="po-empty">Нет доступных сигналов по этому символу</p>
        ) : ( */}
          <div className="sbm-table-selected">
            <div className="sbm-cell">
              <span className="sbm-label">Индикатор</span>
              <span className="sbm-value">
                RSI
              </span>
            </div>
            <div className="sbm-cell">
              <span className="sbm-label">Таймфрейм</span>
              <span className="sbm-value">
                15m
              </span>
            </div>
            <div className="sbm-cell">
              <span className="sbm-label">Значение</span>
              <span className="sbm-value">
                16.64
              </span>
            </div>
            <div className="sbm-cell">
              <span className="sbm-label">Направление</span>
              <span className="sbm-value sbm-badge sbm-badge-up">
                ВВЕРХ
              </span>
            </div>
          </div>

          <div className="sbm-table-wrap">
            <table className="sbm-table">
              <thead>
                <tr>
                  <th>Индикатор</th>
                  <th>Таймфрейм</th>
                  <th>Значение</th>
                  <th>Направление</th>
                </tr>
              </thead>
              <tbody>
                {availableSignals.map((signal, index) => (
                  <tr key={index}>
                    <td>{signal.indicator}</td>
                    <td>{signal.timeframe}</td>
                    <td>{signal.indicatorValue}</td>
                    <td>
                      <span className="sbm-badge sbm-badge-up">
                        {signal.direction}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="sbm-switch-row">
            <button
              type="button"
              className={`sbm-switch ${withCloseCondition ? "active" : ""}`}
              onClick={() => setWithCloseCondition((prev) => !prev)}
              aria-label="Включать автозакрытие"
            >
              <span className="sbm-switch-thumb"></span>
            </button>
            <span className="sbm-switch-label">Включить автозакрытие</span>
          </div>

          <div className="sbm-condition-row">
            <div className="sbm-condition-toggle">
              <button type="button" className="sbm-condition-btn active">
                Меньше
              </button>
              <button type="button" className="sbm-condition-btn">
                Больше
              </button>
            </div>

            <input
              className="sbm-condition-value"
              type="text"
              placeholder="Значение"
              value={targetValue}
              onChange={(e) => setTargetValue(e.target.value)}
            />
          </div>

        {/* {error && <p className="sbm-error-text">{error}</p>}  */}

        <div className="sbm-divider"></div>

        <div className="sbm-footer-actions">
          <button className="sbm-btn cancel" onClick={onClose}>
            Отмена
          </button>
          <button
            className="sbm-btn confirm"
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
