import { cancelOrder } from "../../api/positions";
import { usePositionsStore } from "../../store/usePositionsStore";
import { SymbolLink } from "../../components/ui/SymbolLink";
import { LinkedSignalCell } from "./LinkedSignalCell";
import type { Order } from "../../types/positions";

type OrderRowPorps = {
  order: Order;
  index: number;
}

export function OrderRow({ order, index }: OrderRowPorps) {
  const removeOrder = usePositionsStore((s) => s.removeOrder);
  
  const handleCancel = async () => {
    try {
      await cancelOrder(order.id);
      removeOrder(order.id);
    } catch (err) {
      console.log(`Не удалось отменить ордер ${order.id}:`, err);
    }
  };

  return (
    <tr>
      <td>{index + 1}</td>
      <td>
        <div className="po-symbol">
          <SymbolLink symbol={order.symbol} />
          <span className={`po-direction ${order.side}`}>
            {order.side === "long" ? "Long" : "Short"}
          </span>
        </div>
      </td>
      <td>
        <LinkedSignalCell />
      </td>
      <td>
        <div className="po-actions">
          <button className="po-action-btn close" onClick={handleCancel}>
            Отменить
          </button>
        </div>
      </td>
    </tr>
  );
}