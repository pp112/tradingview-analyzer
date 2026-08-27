import { useEffect } from "react";
import { fetchOrderLinks, fetchPositionLinks } from "../api/signalLinks";
import { useSignalLinksStore } from "../store/useSignalLinksStore";

export function useSignalLinks() {
  const setPositionLinks = useSignalLinksStore((s) => s.setPositionLinks);
  const setOrderLinks = useSignalLinksStore((s) => s.setOrderLinks);

  useEffect(() => {
    Promise.all([fetchPositionLinks(), fetchOrderLinks()])
      .then(([positionLinks, orderLinks]) => {
        setPositionLinks(positionLinks);
        setOrderLinks(orderLinks);
      })
      .catch((err) => {
        console.error("Не удалось загрузить привязки сигналов:", err);
      });
  }, [setPositionLinks, setOrderLinks]);
}
