import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

interface DesktopNavProps {
  className?: string;
  ariaLabel?: string;
  /** Для дубликата: не объявлять вторую копию скринридерам, когда он скрыт. */
  ariaHidden?: boolean;
}

export default function DesktopNav({
  className = "nav-tabs nav-desktop",
  ariaLabel = "Основная навигация",
  ariaHidden = false,
}: DesktopNavProps) {
  const { isAuthenticated } = useAuth();

  return (
    <nav className={className} aria-label={ariaLabel} aria-hidden={ariaHidden || undefined}>
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
  );
}
