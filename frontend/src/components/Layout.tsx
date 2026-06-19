import { Link, Outlet, useLocation } from "react-router-dom";

import DesktopNav from "./DesktopNav";
import MobileBottomNav from "./MobileBottomNav";
import ThemeToggle from "./ThemeToggle";
import { useAuth } from "../context/AuthContext";
import { useFloatingNav } from "../hooks/useFloatingNav";
import { userAvatarLabel, userNickname } from "../utils/avatar";

function isFloatingNavRoute(pathname: string): boolean {
  return pathname === "/" || pathname === "/explore";
}

export default function Layout() {
  const { isAuthenticated, user, logout, loading } = useAuth();
  const { pathname } = useLocation();
  const floatingNavRoute = isFloatingNavRoute(pathname);
  const { active: floatingActive, visible: floatingVisible } = useFloatingNav(floatingNavRoute);

  const floatingNavClass = [
    "nav-tabs nav-desktop nav-desktop--floating",
    floatingActive && "nav-desktop--floating-active",
    floatingActive && !floatingVisible && "nav-desktop--floating-hidden",
  ]
    .filter(Boolean)
    .join(" ");

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

      <DesktopNav />

      <DesktopNav
        className={floatingNavClass}
        ariaLabel="Быстрая навигация при прокрутке"
        ariaHidden={!floatingActive || !floatingVisible}
      />

      <main>
        <Outlet />
      </main>

      <footer className="app-footer">Creavity — одна подписка на весь платный контент платформы</footer>

      <MobileBottomNav isAuthenticated={isAuthenticated} onLogout={() => void logout()} />
    </div>
  );
}
