import { usePositionsData } from "../../hooks/usePositionsData";
import { usePositionsStore } from "../../store/usePositionsStore";
import { OrderRow } from "./OrderRow";
import { PositionRow } from "./PositionRow";

export function PositionsOrdersCard() {
  const positions = usePositionsStore((s) => s.positions);
  const orders = usePositionsStore((s) => s.orders);
  const balance = usePositionsStore((s) => s.balance);
  const { reload } = usePositionsData();

  const totalPnl = positions.reduce((sum, p) => sum + p.pnl, 0);
  
  return (
    <section className="po-card card">
      <div className="po-header">
        <div className="po-title-row">
            <h2 className="po-title">Позиции и ордера</h2>
        </div>
        <div className="po-stats-group">
          <div className="po-stat-divider" />
          <div className="po-stat-item">
            <span className="po-stat-label">Общий PnL</span>
            <div className={`po-stat-value ${totalPnl >=0 ? "pos" : "neg"}`}>
              {totalPnl >= 0 ? "+" : ""}
              {totalPnl.toFixed(2)} 
              <span className="currency">USDT</span>
            </div>
          </div>
          <div className="po-stat-divider" />
          <div className="po-stat-item">
            <span className="po-stat-label">Баланс</span>
            <div className="po-stat-value balance-value">
              {balance !== null ? balance.toFixed(2) : "—"} 
              <span className="currency">USDT</span>
            </div>
          </div>
        </div>
        <button className="po-refresh" onClick={reload}>↻ Обновить</button>
      </div>

      <div className="po-panel">
        <div className="po-table-scroll">
          <table className="po-table po-positions-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Символ</th>
                <th>Нереализ. PnL</th>
                <th>Сигнал</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {positions.length === 0 ? (
                <tr>
                  <td colSpan={5} className="po-empty">Нет открытых позиций</td>
                </tr>
              ) : (
                positions.map((p, i) => <PositionRow key={p.symbol} position={p} index={i} />)
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="po-panel">
        <div className="po-table-scroll">
          <table className="po-table po-orders-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Символ</th>
                <th>Сигнал</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 ? (
                <tr>
                  <td colSpan={4} className="po-empty">Нет открытых ордеров</td>
                </tr>
              ) : (
                orders.map((o, i) => <OrderRow key={o.id} order={o} index={i} />)
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}