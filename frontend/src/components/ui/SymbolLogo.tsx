import { useState } from "react";
import { getSymbolLogoUrl } from "../../utils/symbol";

const SYMBOL_LOGO_SIZE = 18;

interface SymbolLogoProps {
  symbol: string;
}

export function SymbolLogo({ symbol }: SymbolLogoProps) {
  const [failed, setFailed] = useState(false);
  
  if (failed) {
    return (
      <span
        className="sym-logo-fallback"
        style={{ width: SYMBOL_LOGO_SIZE, height: SYMBOL_LOGO_SIZE }}
        >
          {symbol.charAt(0)}
      </span>
    );
  }

  return (
    <img
      src={getSymbolLogoUrl(symbol)}
      alt={symbol}
      width={SYMBOL_LOGO_SIZE}
      height={SYMBOL_LOGO_SIZE}
      className="sym-logo"
      onError={() => setFailed(true)}
      loading="lazy"
    />
  );
}