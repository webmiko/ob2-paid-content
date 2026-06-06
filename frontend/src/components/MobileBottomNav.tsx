import { NavLink } from "react-router-dom";

interface MobileBottomNavProps {
  isAuthenticated: boolean;
  onLogout: () => void;
}

export default function MobileBottomNav({ isAuthenticated, onLogout }: MobileBottomNavProps) {
  return (
    <nav className="mobile-bottom-nav" aria-label="Мобильная навигация">
      <NavLink end className={({ isActive }) => `mobile-nav-item${isActive ? " active" : ""}`} to="/">
        <i className="fa-solid fa-stream" aria-hidden="true" />
        <span>Лента</span>
      </NavLink>
      <NavLink className={({ isActive }) => `mobile-nav-item${isActive ? " active" : ""}`} to="/explore">
        <i className="fa-solid fa-table-cells-large" aria-hidden="true" />
        <span>Каталог</span>
      </NavLink>
      {isAuthenticated ? (
        <>
          <NavLink className={({ isActive }) => `mobile-nav-item${isActive ? " active" : ""}`} to="/profile">
            <i className="fa-solid fa-user" aria-hidden="true" />
            <span>Профиль</span>
          </NavLink>
          <button type="button" className="mobile-nav-item mobile-nav-action" onClick={onLogout}>
            <i className="fa-solid fa-right-from-bracket" aria-hidden="true" />
            <span>Выход</span>
          </button>
        </>
      ) : (
        <>
          <NavLink className={({ isActive }) => `mobile-nav-item${isActive ? " active" : ""}`} to="/login">
            <i className="fa-solid fa-right-to-bracket" aria-hidden="true" />
            <span>Вход</span>
          </NavLink>
          <NavLink className={({ isActive }) => `mobile-nav-item${isActive ? " active" : ""}`} to="/register">
            <i className="fa-solid fa-user-plus" aria-hidden="true" />
            <span>Регистр.</span>
          </NavLink>
        </>
      )}
    </nav>
  );
}
