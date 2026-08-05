import { Badge } from "../../components/ui/Badge";
import { SymbolLink } from "../../components/ui/SymbolLink";
import { volumeClass } from "../../utils/formatters";
import type { CombinedSignal } from "../../types/signal";

type CombinedRowProps = {
  signal: CombinedSignal;
  index: number;
}

export function CombinedRow({ signal, index }: CombinedRowProps) {
  const isBull = signal.direction === "ВВЕРХ";
  const valueClass = isBull ? "value-bull" : "value-bear";
  const badgeVariant = isBull ? "bull" : "bear";

  const cell = (value: number | null) => 
    value !== null ? <span className={valueClass}>{value}</span> : <span className="muted">-</span>;

  return (
    <tr style={{ animationDelay: `${index * 0.03}s` }}>
      <td className="th-fav">☆</td>
      <td className="sym-cell">
        <SymbolLink symbol={signal.symbol} />
      </td>
      <td>{cell(signal.rsi)}</td>
      <td>{cell(signal.macd)}</td>
      <td>{cell(signal.ema_sma)}</td>
      <td>
        <Badge variant={badgeVariant}>{signal.direction}</Badge>
      </td>
      <td>
        <span className={`vol-cell ${volumeClass}`}>{signal.vol_ratio}</span>
      </td>
      <td>
        <span className="corr-cell">${signal.correlation}</span>
      </td>
      <td>
        <span className="chart-btn">График</span>
      </td>
    </tr>
  );
}
