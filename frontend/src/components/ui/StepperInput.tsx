type StepperInputProps = {
  value: number | null;
  step: number;
  min?: number;
  max?: number;
  placeholder?: string;
  formatValue?: (value: number) => string;
  onChange: (value: number | null) => void;
};

export function StepperInput({
  value,
  step,
  min,
  max,
  placeholder,
  formatValue,
  onChange,
}: StepperInputProps) {
  const displayValue = value === null ? "" : formatValue ? formatValue(value) : String(value);

  const clamp = (v: number) => {
    let result = v;
    if (min !== undefined) result = Math.max(min, result);
    if (max !== undefined) result = Math.min(max, result);
    return result;
  };

  const handleStep = (delta: number) => {
    const current = value ?? 0;
    onChange(clamp(current + delta));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.trim().replace(",", ".");

    if (raw === "") {
      onChange(null);
      return;
    }

    const parsed = parseFloat(raw);
    if (!isNaN(parsed)) {
      onChange(clamp(parsed));
    }
  };

  return (
    <div className="corr-box">
      <button className="corr-btn" onClick={() => handleStep(-step)}>−</button>
      <input
        type="text"
        className="corr-input"
        value={displayValue}
        placeholder={placeholder}
        onChange={handleInputChange}
      />
      <button className="corr-btn" onClick={() => handleStep(step)}>+</button>
    </div>
  );
}