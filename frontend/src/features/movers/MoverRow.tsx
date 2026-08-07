import { SymbolLink } from "../../components/ui/SymbolLink";

type MoverRowProps = {
  index: number;
  symbol: string;
  value: string;
  valueClassName: string;
};

export function MoverRow({ index, symbol, value, valueClassName }: MoverRowProps) {
  return (
    <div className="mover-row">
      <span className="mover-index">{index + 1}</span>
      <span className="mover-sym">
        <SymbolLink symbol={symbol} />
      </span>
      <span className={`mover-pct ${valueClassName}`}>{value}</span>
    </div>
  );
}
