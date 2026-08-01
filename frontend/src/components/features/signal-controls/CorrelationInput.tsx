import { useFiltersStore } from "../../../store/useFiltersStore";
import { StepperInput } from "../../ui/StepperInput"

function formatCorrelation(value: number): string {
  return value.toFixed(2).replace(/\.00$/, "");
}

export function CorrelationInput() {
  const correlation = useFiltersStore((s) => s.correlation);
  const setCorrelation = useFiltersStore((s) => s.setCorrelation)

  return (
    <div className="control-group control-group--filters">
      <span className="control-label control-label-centered">Корреляция</span>
      <StepperInput
        value={correlation}
        step={0.05}
        min={-1}
        max={1}
        formatValue={formatCorrelation}
        onChange={(value) => setCorrelation(value ?? 1)}
      />
    </div>
  );
}