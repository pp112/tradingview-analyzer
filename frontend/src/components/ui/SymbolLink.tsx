interface SymbolLinkProps {
  symbol: string;
}

export function SymbolLink({ symbol }: SymbolLinkProps) {
  const formatted = symbol.replace("/", "");

  return (
    <a
      href={`https://ru.tradingview.com/chart/?symbol=BYBIT:${formatted}.P`}
      target="_blank"
      className="sym-link"
    >
      {symbol}
    </a>
  );
}
