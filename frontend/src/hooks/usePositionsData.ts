import { useCallback, useEffect } from "react";
import { fetchBalance, fetchOrders, fetchPositions } from "../api/positions";
import { usePositionsStore } from "../store/usePositionsStore";

const POLL_INTERVAL_MS = 5000;

export function usePositionsData() {
  const setPositions = usePositionsStore((s) => s.setPositions);
  const setOrders = usePositionsStore((s) => s.setOrders);
  const setBalance = usePositionsStore((s) => s.setBalance);
  const setUpdatedAt = usePositionsStore((s) => s.setUpdatedAt);

  const load = useCallback(async () => {
    try {
      const [positions, orders, balance] = await Promise.all([
        fetchPositions(),
        fetchOrders(),
        fetchBalance(),
      ]);
      setPositions(positions);
      setOrders(orders);
      setBalance(balance.balance);
      setUpdatedAt(Date.now());
    } catch (err) {
      console.error("Не удалось загрузить позиции/ордера:", err);
    }
  }, [setPositions, setOrders, setBalance, setUpdatedAt]);

  useEffect(() => {
    load();

    const intervalId = setInterval(load, POLL_INTERVAL_MS);

    return () => {
      clearInterval(intervalId);
    }
  }, [load]);

}
