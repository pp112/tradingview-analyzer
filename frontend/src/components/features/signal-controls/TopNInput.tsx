import { useFiltersStore } from "../../../store/useFiltersStore";
import { StepperInput } from "../../ui/StepperInput";

export function TopNInput() {
  const topN = useFiltersStore((s) => s.topN);
  const setTopN = useFiltersStore((s) => s.setTopN);

  return (
    <div className="control-group control-group--topn">
      <span className="control-label control-label-centered">Количество</span>
      <StepperInput
        value={topN}
        step={1}
        min={1}
        placeholder="Все"
        onChange={setTopN}
      />
    </div>
  );
}
