import { useFiltersStore } from "../../store/useFiltersStore";
import type { IndicatorType, Sigtype, SortColumn } from "../../types/signal";

type ColumnDef = {
  key: SortColumn;
  label: string;
};

export function SignalTableHeader() {
  const sigtype = useFiltersStore((s) => s.sigtype);
  const indicator = useFiltersStore((s) => s.indicator);
  const sort = useFiltersStore((s) => s.sort);
  const toggleSort = useFiltersStore((s) => s.toggleSort);

  const columns = getColumns(sigtype, indicator);

  return (
    <tr>
      <th className="th-fav">★</th>
      {columns.map((col) => (
        <th
          key={col.key}
          className={
            sort.column === col.key
              ? sort.direction === 1
                ? "sorted-desc"
                : sort.direction === 2
                  ? "sorted-asc"
                  : ""
              : ""
          }
          onClick={() => toggleSort(col.key)}
        >
          {col.label}
          <span className="sort-icon" />
        </th>
      ))}
      <th>Подробно</th>
    </tr>
  );
}

function getColumns(
  sigtype: Sigtype,
  indicator: IndicatorType | null,
): ColumnDef[] {
  if (sigtype === "combined") {
    return [
      { key: "symbol", label: "Монета" },
      { key: "rsi", label: "RSI" },
      { key: "macd", label: "MACD" },
      { key: "emaSma", label: "EMA-SMA" },
      { key: "direction", label: "Направление" },
      { key: "volRatio", label: "VOLUME" },
      { key: "correlation", label: "Корреляция" },
    ];
  }

  if (indicator === "volRatio") {
    return [
      { key: "symbol", label: "Монета" },
      { key: "volRatio", label: "Значение" },
      { key: "indicator", label: "Индикатор" },
      { key: "correlation", label: "Корреляция" },
    ];
  }

  return [
    { key: "symbol", label: "Монета" },
    { key: "indicatorValue", label: "Значение" },
    { key: "indicator", label: "Индикатор" },
    { key: "direction" as SortColumn, label: "Направление" },
    { key: "volRatio" as SortColumn, label: "Объем" },
    { key: "correlation", label: "Корреляция" },
  ];
}
