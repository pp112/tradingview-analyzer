import { Badge } from "../../components/ui/Badge";
import { SymbolLink } from "../../components/ui/SymbolLink";
import { useFiltersStore } from "../../store/useFiltersStore";
import { formatValue, volumeClass } from "../../utils/formatters";
import type { Signal } from "../../types/signal";

type SignalRowProps = {
  signal: Signal;
  index: number;
};

export function SignalRow({ signal, index }: SignalRowProps) {
  const indicator = useFiltersStore((s) => s.indicator);
  const isVolume = indicator === "vol_ratio";
  const volClass = volumeClass(signal.vol_ratio);
  const isBull = signal.direction === "ВВЕРХ";
  const valueClass = isBull ? "value-bull" : "value-bear";
  const badgeVariant = isBull ? "bull" : "bear";

  return (
    <tr style={{ animationDelay: `${index * 0.03}s` }}>
      <td className="th-fav">☆</td>
      <td className="sym-cell">
        <SymbolLink symbol={signal.symbol} />
      </td>

      {isVolume ? (
        <>
          <td>
            <span className={`vol-cell ${volClass}`}>{signal.vol_ratio}</span>
          </td>
          <td>
            <Badge variant="volume">VOLUME</Badge>
          </td>
        </>
      ) : (
        <>
          <td>
            <span className={valueClass}>
              {formatValue(signal.indicator_value)}
            </span>
          </td>
          <td>
            <Badge variant={badgeVariant}>
              {signal.indicator.toUpperCase().replace("_", "-")}
            </Badge>
          </td>
          <td>
            <Badge variant={badgeVariant}>{signal.direction}</Badge>
          </td>
          <td>
            <span className={`vol-cell ${volClass}`}>{signal.vol_ratio}</span>
          </td>
        </>
      )}

      <td>{signal.correlation}</td>
      <td>
        <span className="chart-btn">График</span>
      </td>
    </tr>
  );
}
