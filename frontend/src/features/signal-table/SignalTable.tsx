import { useFilteredSignals } from "../../hooks/useFilteredSignals";
import { useFiltersStore } from "../../store/useFiltersStore";
import { CombinedRow } from "./CombinedRow";
import { SignalRow } from "./SignalRow";
import { SignalTableHeader } from "./SignalTableHeader";
import type { CombinedSignal, Signal } from "../../types/signal";
import { useSignalsStore } from "../../store/useSignalsStore";

export function SignalTable() {
  const sigtype = useFiltersStore((s) => s.sigtype);
  const connectionStatus = useSignalsStore((s) => s.connectionStatus);
  const rows = useFilteredSignals();

  return (
    <div className="table-wrap">
      <table className="signal-table">
        <thead>
          <SignalTableHeader />
        </thead>
        <tbody>
          {connectionStatus === "connecting" ? (
            <tr>
              <td colSpan={8} className="loading-cell">
                <div className="loader" />
                <span>Загрузка сигналов...</span>
              </td>
            </tr>
          ) : connectionStatus === "error" ? (
            <tr>
              <td colSpan={8} className="loading-cell">
                Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.
              </td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={8} className="loading-cell">
                Нет данных для выбранных фильтров
              </td>
            </tr>
          ) : sigtype === "combined" ? (
            (rows as CombinedSignal[]).map((row, i) => (
              <CombinedRow key={row.symbol} signal={row} index={i} />
            ))
          ) : (
            (rows as Signal[]).map((row, i) => (
              <SignalRow
                key={`${row.symbol}-${row.indicator}-${i}`}
                signal={row}
                index={i}
              />
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
