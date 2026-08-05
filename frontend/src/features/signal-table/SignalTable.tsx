import { useFilteredSignals } from "../../hooks/useFilteredSignals";
import { useFiltersStore } from "../../store/useFiltersStore";
import { CombinedRow } from "./CombinedRow";
import { SignalRow } from "./SignalRow";
import { SignalTableHeader } from "./SignalTableHeader";
import type { CombinedSignal, Signal } from "../../types/signal";

export function SignalTable() {
  const sigtype = useFiltersStore((s) => s.sigtype);
  const rows = useFilteredSignals();

  return (
    <div className="table-wrap">
      <table className="signal-table">
        <thead>
          <SignalTableHeader />
        </thead>
        <tbody>
          {rows.length === 0 ? (
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
