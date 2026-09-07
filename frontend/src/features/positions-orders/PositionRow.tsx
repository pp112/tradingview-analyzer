import { useState } from "react";
import { closePosition } from "../../api/positions";
import { SymbolLink } from "../../components/ui/SymbolLink";
import { usePositionsStore } from "../../store/usePositionsStore";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import type { Position } from "../../types/positions";
import { LinkedSignalCell } from "./LinkedSignalCell";
import { unlinkSignalFromPosition } from "../../api/signalLinks";
import { SignalBindModal } from "./SignalBindModal";

type PositionRowProps = {
  position: Position;
  index: number;
};

export function PositionRow({ position, index }: PositionRowProps) {
  const removePosition = usePositionsStore((s) => s.removePosition);
  const removePositionLink = useSignalLinksStore((s) => s.removePositionLink);
  const link = useSignalLinksStore((s) => 
    s.positionLinks.find((l) => l.symbol === position.symbol)
  );

  const [showModal, setShowModal] = useState(false);
  const isProfit = position.pnl >= 0;

  const handleClose = async () => {
    try {
      await closePosition(position.symbol);
      removePosition(position.symbol);
    } catch (err) {
      console.error(`Не удалось закрыть позицию ${position.symbol}:`, err);
    }
  };

  const handleUnbind = async () => {
    if (!link) return;
    try {
      await unlinkSignalFromPosition(link.id);
      removePositionLink(link.id);
    } catch (err) {
      console.error(`Не удалось отвязать сигнал от позиции ${position.symbol}:`, err);
    }
  };
  
  return (
    <>
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
            {position.pnl.toFixed(2)} USDT
            ({isProfit ? "+" : ""}
            {position.pnlPct}%)
          </span>
        </td>
        <td>
          <LinkedSignalCell
            link={link}
            onBindClick={() => setShowModal(true)}
            onUnbindClick={handleUnbind}
          />
        </td>
        <td>
          <div className="po-actions">
            <button className="po-action-btn close" onClick={handleClose}>
              Закрыть
            </button>
          </div>
        </td>
      </tr>

      {showModal && (
        <SignalBindModal
          symbol={position.symbol}
          entityType="position"
          direction={position.side === "long" ? "ВВЕРХ" : "ВНИЗ"}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}
