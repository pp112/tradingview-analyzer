import { useCallback, useEffect } from "react";
import { fetchBalance, fetchOrders, fetchPositions } from "../api/positions";
import { usePositionsStore } from "../store/usePositionsStore";

const POLL_INTERVAL_MS = 5000;

export function usePositionsData() {
  const setPositions = usePositionsStore((s) => s.setPositions);
  const setOrders = usePositionsStore((s) => s.setOrders);
  const setBalance = usePositionsStore((s) => s.setBalance);
  const setStatus = usePositionsStore((s) => s.setStatus);

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
      setStatus("loaded");
    } catch (err) {
      console.error("Не удалось загрузить позиции/ордера:", err);
      setStatus("error");
    }
  }, [setPositions, setOrders, setBalance, setStatus]);

  useEffect(() => {
    setStatus("loading");
    load();

    const intervalId = setInterval(load, POLL_INTERVAL_MS);

    return () => {
      clearInterval(intervalId);
    }
  }, [load, setStatus]);

  return { reload: load };
}
