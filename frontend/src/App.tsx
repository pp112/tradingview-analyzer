import { useEffect, useState } from "react";
import { Sidebar } from "./components/layout/Sidebar";
import { Topbar } from "./components/layout/Topbar";
import { SignalControls } from "./features/signal-controls/SignalControls";
import { SignalTable } from "./features/signal-table/SignalTable";
import { useSSE } from "./hooks/useSSE";
import { fetchInitialData } from "./api/signals";
import { useSignalsStore } from "./store/useSignalsStore";
import { MoversCard } from "./features/movers/MoversCard";

const PAGE_TITLES: Record<string, string> = {
  home: "Главная",
};

export default function App() {
  const [activePage, setActivePage] = useState("signals");
  const setAllSignals = useSignalsStore((s) => s.setAllSignals);
  const setPriceVolume = useSignalsStore((s) => s.setPriceVolume);
  const setConnectionStatus = useSignalsStore((s) => s.setConnectionStatus);

  useSSE();

  useEffect(() => {
    fetchInitialData()
      .then((data) => {
        setAllSignals(data.signals);
        if (data.price_changes) {
          setPriceVolume(data.price_changes);
        }
        setConnectionStatus("connected");
      })
      .catch((err) => {
        console.error("Не удалось загрузить начальные данные:", err);
        setConnectionStatus("error");
      });
  }, [setAllSignals, setPriceVolume, setConnectionStatus]);

  return (
    <>
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      <main className="main">
        <Topbar title={PAGE_TITLES[activePage] ?? "CryptoScope"} />

        <div className="content">
          <div className="panel-left">
            <SignalControls />
            <SignalTable />
            
            <div className="bottom-row">
              <MoversCard title="Топ рост" variant="gainers" />
              <MoversCard title="Топ падение" variant="losers" />
              <MoversCard title="Всплески объема" variant="volume" />
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
