type NavItem = {
  page: string;
  icon: string;
  label: string;
};

const NAV_ITEMS: NavItem[] = [
  { page: "home", icon: "⬡", label: "Главная" },
  { page: "watchlist", icon: "✦", label: "Watchlist" },
  { page: "settings", icon: "◈", label: "Настройки" },
];

type SidebarProps = {
  activePage: string;
  onNavigate: (page: string) => void;
};

export function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar" id="sidebar">
      <div className="logo">
        <div className="logo-icon">◈</div>
        <span className="logo-text">CryptoScope</span>
      </div>
      <nav className="nav">
        {NAV_ITEMS.map((item) => (
          <a
            key={item.page}
            className={`nav-item ${activePage === item.page ? "active" : ""}`}
            onClick={() => onNavigate(item.page)}
          >
            <span className="nav-icon">{item.icon}</span> {item.label}
          </a>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="conn-block">
          <div className="conn-label">Подключение</div>
          <div className="conn-badge">
            <span className="conn-dot"></span>
            <span>Bybit · Подключено</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
