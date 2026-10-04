import { useMemo, useState } from "react";
import { useSignalsStore } from "../../store/useSignalsStore";
import type { Direction, IndicatorType, Signal, Timeframe } from "../../types/signal";
import type {
  CloseConditionInput,
  CloseOperator,
  OrderSignalLinkResponse,
  PositionSignalLinkResponse,
} from "../../types/signalLinks";
import { linkSignalToOrder, linkSignalToPosition } from "../../api/signalLinks";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import { ChartNoAxesCombined, Check, Link, ArrowUp, X, ArrowDown, PenLine } from "lucide-react";
import { SymbolLogo } from "../../components/ui/SymbolLogo";
import { createPortal } from "react-dom";

type EntityType = "position" | "order";

type LinkType = PositionSignalLinkResponse | OrderSignalLinkResponse;

type SignalBindModalProps = {
  symbol: string;
  entityType: EntityType;
  exchangeOrderId?: string;
  direction: Direction;
  existingLink?: LinkType;
  onClose: () => void;
};

type AvailableSignals = Signal & {
  timeframe: Timeframe;
};

const signalKey = (indicator: IndicatorType, timeframe: Timeframe, value: number) =>
  `${indicator}:${timeframe}:${value}`

export function SignalBindModal({
  symbol,
  entityType,
  exchangeOrderId,
  direction,
  existingLink,
  onClose,
}: SignalBindModalProps) {
  const allSignals = useSignalsStore((s) => s.signals);
  const addPositionLink = useSignalLinksStore((s) => s.addPositionLink);
  const addOrderLink = useSignalLinksStore((s) => s.addOrderLink);

  const isEdit = existingLink !== undefined;
  const existingLinkedSignalKey = existingLink
    ? signalKey(existingLink.signal.indicator, existingLink.signal.timeframe, existingLink.signal.value)
    : null;

  const [selectedKey, setSelectedKey] = useState<string | null>(existingLinkedSignalKey);
  const [withCloseCondition, setWithCloseCondition] = useState(
    existingLink ? existingLink.closeCondition !== null : true
  );
  const [closeOperator, setCloseOperator] = useState<CloseOperator>(
    existingLink?.closeCondition?.operator ?? "<="
  );
  const [targetValue, setTargetValue] = useState(
    existingLink?.closeCondition
    ? String(existingLink.closeCondition.targetValue)
    : ""
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const existingLinkedSignal = useMemo<AvailableSignals | null>(() => {
    if (!existingLink) return null;
    const { indicator, timeframe, value, direction } = existingLink.signal;
    return {
      symbol,
      indicator,
      timeframe,
      direction,
      indicatorValue: value,
      volRatio: value,
      correlation: 0,
    };
  }, [existingLink, symbol]);

  const availableSignals = useMemo(() => {
    const result: AvailableSignals[] = [];

    for (const [timeframe, list] of Object.entries(allSignals)) {
      if (!list) continue;
      result.push(
        ...list
          .filter((s) => s.symbol === symbol && s.direction === direction)
          .map((signal) => ({
            ...signal,
            timeframe: timeframe as Timeframe,
          })),
      );
    }

    if (
      existingLinkedSignal && 
      !result.some((s) => signalKey(s.indicator, s.timeframe, s.indicatorValue) === existingLinkedSignalKey)
    ) {
      result.push(existingLinkedSignal);
    }

    return result.sort((a, b) => {
      const aIsExisting = signalKey(a.indicator, a.timeframe, a.indicatorValue) === existingLinkedSignalKey;
      const bIsExisting = signalKey(b.indicator, b.timeframe, b.indicatorValue) === existingLinkedSignalKey;

      if (aIsExisting !== bIsExisting) return aIsExisting ? -1 : 1;

      return b.indicator.localeCompare(a.indicator)
    });
  }, [allSignals, symbol, direction, existingLinkedSignal, existingLinkedSignalKey]);

  const selected = useMemo<AvailableSignals | null>(() => {
    if (!selectedKey) return null;

    if (selectedKey === existingLinkedSignalKey) return existingLinkedSignal;

    return (
      availableSignals.find(
        (s) => signalKey(s.indicator, s.timeframe, s.indicatorValue) === selectedKey  
      ) ?? null
    );
  }, [availableSignals, selectedKey, existingLinkedSignal, existingLinkedSignalKey])

  const hasContent = availableSignals.length > 0;

  const handleConfirm = async () => {
    if (!selected) {
      setError("Выберите сигнал перед привязкой");
      return;
    }

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

  return createPortal(
    <div className="sbm">
      <div className="sbm-backdrop" onClick={onClose} />
      <div className="sbm-dialog" role="dialog" aria-modal="true">
        <div className="sbm-header">
          <div className="sbm-title">
            <span className="sbm-header-icon">
              {isEdit
                ? <PenLine size={24} strokeWidth={2.5} /> 
                : <Link size={24} strokeWidth={2.5} />
              }
            </span>
            <div className="sbm-header-text">
              <div className="sbm-header-title">
                {isEdit ? "Изменить сигнал" : "Привязать сигнал"}
              </div>
              <div className="sbm-symbol-line">
                <SymbolLogo symbol={symbol} /> 
                <span>{symbol}</span>
              </div>
            </div>
          </div>
          <button className="sbm-close" onClick={onClose}>
            <X size={16} strokeWidth={2.6} />
          </button>
        </div>

        {!hasContent ? (
          <div className="sbm-empty" role="status">
            <span className="sbm-empty-icon" aria-hidden="true">
              <ChartNoAxesCombined size={20} />
            </span>
            <div>
              <p className="sbm-empty-title">Сигналы не найдены</p>
              <p className="sbm-empty-description">
                Для {symbol} пока нет доступных сигналов
              </p>
            </div>
          </div>
        ) : (
          <>
            <div className="sbm-selected-row">
              <div className="sbm-cell">
                <span className="sbm-label">Индикатор</span>
                <span className="sbm-value">
                  {selected?.indicator ?? ""}
                </span>
              </div>
              <div className="sbm-selected-divider"></div>
              <div className="sbm-cell">
                <span className="sbm-label">Таймфрейм</span>
                <span className="sbm-value">
                  {selected?.timeframe ?? ""}
                </span>
              </div>
              <div className="sbm-selected-divider"></div>
              <div className="sbm-cell">
                <span className="sbm-label">Значение</span>
                <span className="sbm-value">
                  {selected?.indicatorValue ?? ""}
                </span>
              </div>
              <div className="sbm-selected-divider"></div>
              <div className="sbm-cell">
                <span className="sbm-label">Направление</span>
                <span 
                  className={`sbm-value sbm-badge ${
                    selected?.direction === "ВВЕРХ"
                      ? "sbm-badge-up"
                      : selected?.direction === "ВНИЗ"
                        ? "sbm-badge-down"
                        : ""
                  }`}
                >
                  {selected && (
                    selected.direction === "ВВЕРХ"
                      ? <ArrowUp size={20} strokeWidth={2.5} />
                      : <ArrowDown size={20} strokeWidth={2.5} />
                  )}
                  <span>
                    {selected?.direction ?? ""}
                  </span>
                </span>
              </div>
            </div>
            
            <div className="sbm-controls">
              <div className="sbm-table-wrap">
                <table className="sbm-table">
                  <thead>
                    <tr>
                      <th>Индикатор</th>
                      <th>Таймфрейм</th>
                      <th>Значение</th>
                      <th>Направление</th>
                      <th className="sbm-check-cell"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {availableSignals.map((signal) => {
                      const key = signalKey(signal.indicator, signal.timeframe, signal.indicatorValue);
                      const isSelected = key === selectedKey;
                      return (
                        <tr 
                          key={key}
                          className={isSelected ? "selected" : ""}
                          onClick={() => {
                            setSelectedKey((prev) => prev === key ? null : key);
                            setError(null);
                          }}
                        >
                          <td>
                            <div className="sbm-indicator-cell">
                              <span className={`sbm-indicator-icon sbm-indicator-icon--${signal.indicator}`}>
                                <ChartNoAxesCombined size={15} strokeWidth={2.7}/>
                              </span>
                              <span>
                                {signal.indicator}
                              </span>
                            </div>
                          </td>
                          <td>{signal.timeframe}</td>
                          <td>{signal.indicatorValue}</td>
                          <td>
                            <span 
                              className={`sbm-badge ${
                                signal.direction === "ВВЕРХ" 
                                  ? "sbm-badge-up" 
                                  : "sbm-badge-down"
                              }`}
                            >
                              {signal.direction === "ВВЕРХ"
                                ? <ArrowUp size={16} strokeWidth={2.5} />
                                : <ArrowDown size={16} strokeWidth={2.5} />}
                              <span>
                                {signal.direction}
                              </span>
                            </span>
                          </td>
                          <td className="sbm-check-cell">
                            {isSelected && (
                              <span className="sbm-check-icon">
                                <Check size={14} strokeWidth={2.5}/>
                              </span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              
              <div className="sbm-close-controls">
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
                  <div className="sbm-condition-toggle" data-operator={closeOperator}>
                    <button 
                      type="button" 
                      className={`sbm-condition-btn ${closeOperator === "<=" ? "active" : ""}`}
                      onClick={() => setCloseOperator("<=")}
                    >
                      Меньше
                    </button>
                    <button 
                      type="button"
                      className={`sbm-condition-btn ${closeOperator === ">=" ? "active" : ""}`}
                      onClick={() => setCloseOperator(">=")}
                    >
                      Больше
                    </button>
                  </div>

                  <input
                    className="sbm-condition-value"
                    type="text"
                    placeholder="Значение"
                    value={targetValue}
                    disabled={!withCloseCondition}
                    onChange={(e) => setTargetValue(e.target.value)}
                  />
                </div>
              </div>
            </div>
          </>
        )}

        {error && <p className="sbm-error-text">{error}</p>} 

        <div className="sbm-footer-divider"></div>

        <div className="sbm-footer-actions">
          <button className="sbm-btn cancel" onClick={onClose}>
            {hasContent ? "Отмена" : "Закрыть"}
          </button>
          {hasContent && (
            <button
              className="sbm-btn confirm"
              onClick={handleConfirm}
              disabled={loading}
            >
              {loading 
                ? isEdit ? "Сохранение..." : "Привязка..."
                : isEdit ? "Изменить" : "Привязать сигнал"}
            </button>
          )}
        </div>
      </div>
    </div>,
    document.body,
  );
}
