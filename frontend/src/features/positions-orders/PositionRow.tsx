import { closePosition } from "../../api/positions";
import { SymbolLink } from "../../components/ui/SymbolLink";
import { usePositionsStore } from "../../store/usePositionsStore";
import type { Position } from "../../types/positions";
import { LinkedSignalCell } from "./LinkedSignalCell";

type PositionRowProps = {
  position: Position;
  index: number;
};

export function PositionRow({ position, index }: PositionRowProps) {
  const removePosition = usePositionsStore((s) => s.removePosition);
  const isProfit = position.pnl >= 0;

  const handleClose = async () => {
    try {
      await closePosition(position.symbol);
      removePosition(position.symbol);
    } catch (err) {
      console.error(`Не удалось закрыть позицию ${position.symbol}:`, err);
    }
  };
  
  return (
    <tr>
      <td>{index + 1}</td>
      <td>
        <div className="po-symbol">
          <SymbolLink symbol={position.symbol} />
          <span className={`po-direction ${position.side}`}>
            {position.side === "long" ? "Long" : "Short"}
          </span>
        </div>
      </td>
      <td>
        <span className={`po-pnl ${isProfit ? "pos" : "neg"}`}>
          {isProfit ? "+" : ""}
          {position.pnl} USDT
          <small>
            ({isProfit ? "+" : ""}
            {position.pnlPct}%)
          </small>
        </span>
      </td>
      <td>
        <LinkedSignalCell />
      </td>
      <td>
        <div className="po-actions">
          <button className="po-action-btn close" onClick={handleClose}>
            Закрыть
          </button>
        </div>
      </td>
    </tr>
  );
}
