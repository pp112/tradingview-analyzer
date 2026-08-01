import { useFiltersStore } from "../../../store/useFiltersStore";
import type { Sigtype } from "../../../types/signal";

const SIGTYPES: { value: Sigtype, label: string }[] = [
  { value: "all", label: "Все" },
  { value: "strong", label: "Сильные" },
  { value: "combined", label: "Комбинированные" },
];

export function SigtypeSwitch() {
  const sigtype = useFiltersStore((s) => s.sigtype);
  const setSigtype = useFiltersStore((s) => s.setSigtype);

  return (
    <div className="control-group control-group--sigtype">
      <span className="control-label">Тип сигнала</span>
      <div className="control-buttons">
        {SIGTYPES.map((st) => (
          <button
            key={st.value}
            className={`btn btn--sigtype ${sigtype === st.value ? "active" : ""}`}
            onClick={() => setSigtype(st.value)}
          >
            {st.label}
          </button>
        ))}
      </div>
    </div>
  );
}