export function getBaseAsset(symbol: string): string {
  return symbol.split("/")[0];
}

export function getSymbolLogoUrl(symbol: string): string {
  return `https://s3-symbol-logo.tradingview.com/crypto/XTVC${getBaseAsset(symbol)}.svg`;
}