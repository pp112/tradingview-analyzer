import { CorrelationInput } from "./CorrelationInput";
import { IndicatorSwitch } from "./IndicatorSwitch";
import { SigtypeSwitch } from "./SigtypeSwitch";
import { TimeframeSwitch } from "./TimeframeSwitch";
import { TopNInput } from "./TopNInput";

export function SignalControls() {
  return (
    <div className="controls-row">
      <TimeframeSwitch />
      <IndicatorSwitch />
      <SigtypeSwitch />
      <CorrelationInput />
      <TopNInput />
    </div>
  );
}