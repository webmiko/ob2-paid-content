import { Link, NavLink, Outlet } from "react-router-dom";

import MobileBottomNav from "./MobileBottomNav";
import ThemeToggle from "./ThemeToggle";
import { useAuth } from "../context/AuthContext";
import { userAvatarLabel, userNickname } from "../utils/avatar";

export default function Layout() {
  const { isAuthenticated, user, logout, loading } = useAuth();

  return (
    <div className="app-container">
      <div className="ambient-glow" aria-hidden="true" />
      <header className="top-bar">
        <Link className="logo-link" to="/">
          <p className="logo-title">
            <i className="fa-solid fa-pen-fancy" aria-hidden="true" /> Creavity
          </p>
          <span className="logo-tagline">Платформа авторов и платного контента</span>
        </Link>

        <div className="user-controls">
          <ThemeToggle />
          {loading ? (
            <span className="user-controls-skeleton" aria-hidden="true" />
          ) : isAuthenticated && user ? (
            <>
              <div className="user-avatar" aria-hidden="true">
                {userAvatarLabel(user.display_name, user.phone)}
              </div>
              <span className="user-nickname">{userNickname(user.display_name)}</span>
              <button
                type="button"
                className="btn-pill btn-sm-pill btn-pill-secondary desktop-only"
                onClick={() => void logout()}
              >
                Выйти
              </button>
            </>
          ) : (
            <span className="text-muted guest-label">Гость</span>
          )}
        </div>
      </header>

      <nav className="nav-tabs nav-desktop" aria-label="Основная навигация">
        <NavLink end className={({ isActive }) => `nav-btn${isActive ? " active" : ""}`} to="/">
          <i className="fa-solid fa-stream" aria-hidden="true" />
          Лента
        </NavLink>
        <NavLink className={({ isActive }) => `nav-btn${isActive ? " active" : ""}`} to="/explore">
          <i className="fa-solid fa-table-cells-large" aria-hidden="true" />
          Каталог
        </NavLink>
        {isAuthenticated ? (
          <NavLink className={({ isActive }) => `nav-btn${isActive ? " active" : ""}`} to="/profile">
            <i className="fa-solid fa-user" aria-hidden="true" />
            Профиль
          </NavLink>
        ) : (
          <>
            <NavLink className={({ isActive }) => `nav-btn${isActive ? " active" : ""}`} to="/login">
              <i className="fa-solid fa-right-to-bracket" aria-hidden="true" />
              Вход
            </NavLink>
            <NavLink className={({ isActive }) => `nav-btn${isActive ? " active" : ""}`} to="/register">
              <i className="fa-solid fa-user-plus" aria-hidden="true" />
              Регистрация
            </NavLink>
          </>
        )}
      </nav>

      <main>
        <Outlet />
      </main>

      <footer className="app-footer">Creavity — одна подписка на весь платный контент платформы</footer>

      <MobileBottomNav isAuthenticated={isAuthenticated} onLogout={() => void logout()} />
    </div>
  );
}
