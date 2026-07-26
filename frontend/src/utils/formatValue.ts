export function formatValue(num: number): number {
  if (num === 0) return 0;

  const abs = Math.abs(num);
  const decimals = abs >= 1 ? 2 : Math.ceil(-Math.log10(abs)) + 1;

  return Number(num.toFixed(decimals));
}