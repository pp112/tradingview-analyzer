import { MarketSessions } from "../../features/market-sessions/MarketSessions";

type NavItem = {
  page: string;
  label: string;
};

const NAV_ITEMS: NavItem[] = [
  { page: "home", label: "Главная" },
  { page: "settings", label: "Настройки" },
];

type TopbarProps = {
  activePage: string;
  onNavigate: (page: string) => void;
};

export function Topbar({ activePage, onNavigate }: TopbarProps) {
  return (
    <header className="topbar">
      <div className="logo">
        <div className="logo-icon">◈</div>
        <span className="logo-text">CryptoScope</span>
      </div>
      
      <nav className="topnav">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.page}
            type="button"
            className={`topnav-item ${activePage === item.page ? "active" : ""}`}
            onClick={() => onNavigate(item.page)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <MarketSessions />
    </header>
  );
}
