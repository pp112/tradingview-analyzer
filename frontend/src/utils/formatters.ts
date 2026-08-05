export function formatValue(num: number): number {
  if (num === 0) return 0;

  const abs = Math.abs(num);
  const decimals = abs >= 1 ? 2 : Math.ceil(-Math.log10(abs)) + 1;

  return Number(num.toFixed(decimals));
}

export function volumeClass(volRatio: number): string {
  if (volRatio >= 4) return "vol-red";
  if (volRatio >= 3) return "vol-orange";
  if (volRatio >= 2) return "vol-yellow";
  return "vol-default";
}