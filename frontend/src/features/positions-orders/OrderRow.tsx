import { cancelOrder } from "../../api/positions";
import { usePositionsStore } from "../../store/usePositionsStore";
import { SymbolLink } from "../../components/ui/SymbolLink";
import { LinkedSignalCell } from "./LinkedSignalCell";
import type { Order } from "../../types/positions";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";
import { useRef, useState } from "react";
import { unlinkSignalFromOrder } from "../../api/signalLinks";
import { SignalBindModal } from "./SignalBindModal";
import { X } from "lucide-react";
import { formatTimeAgo } from "../../utils/formatTimeAgo";
import { ConfirmPopover } from "../../components/ui/ConfirmPopover";

type OrderRowPorps = {
  order: Order;
  index: number;
  now: number;
}

export function OrderRow({ order, index, now }: OrderRowPorps) {
  const removeOrder = usePositionsStore((s) => s.removeOrder);
  const removeOrderLink = useSignalLinksStore((s) => s.removeOrderLink);
  const link = useSignalLinksStore((s) =>
    s.orderLinks.find((l) => l.order_id === order.id)
  );

  const [showModal, setShowModal] = useState(false);
  const [confirmCancel, setConfirmCancel] = useState(false);

  const cancelBtnRef = useRef<HTMLButtonElement>(null);
  
  const handleCancel = async () => {
    try {
      await cancelOrder(order.id);
      removeOrder(order.id);
    } catch (err) {
      console.log(`Не удалось отменить ордер ${order.id}:`, err);
    }
  };

  const handleUnbind = async () => {
    if (!link) return;
    try {
      await unlinkSignalFromOrder(link.id);
      removeOrderLink(link.id);
    } catch (err) {
      console.error(`Не удалось отвязать сигнал от ордера ${order.id}:`, err);
    }
  }

  return (
    <>
      <tr>
        <td>{index + 1}</td>
        <td>
          <div className="po-symbol">
            <SymbolLink symbol={order.symbol} />
            <span className={`po-direction ${order.side}`}>
              {order.side === "long" ? "Long" : "Short"}
            </span>
          </div>
          <span className="po-created-at" title={new Date(order.createdAt).toLocaleString("ru-RU")}>
            {formatTimeAgo(order.createdAt, now)}
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
            <button
              ref={cancelBtnRef}
              className="po-btn action" 
              onClick={() => setConfirmCancel((prev) => !prev)}
              title="Отменить ордер"  
            >
              <X size={14} strokeWidth={2.5} />
            </button>
            {confirmCancel && (
              <ConfirmPopover 
                anchorRef={cancelBtnRef}
                message="Отменить ордер?"
                onConfirm={() => {
                  setConfirmCancel(false);
                  handleCancel();
                }}
                onCancel={() => setConfirmCancel(false)}
              />
            )}
          </div>
        </td>
      </tr>

      {showModal && (
        <SignalBindModal
          symbol={order.symbol}
          entityType="order"
          orderId={order.id}
          direction={order.side === "long" ? "ВВЕРХ" : "ВНИЗ"}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}