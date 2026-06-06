import { Link, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
        <div className="container">
          <Link className="navbar-brand" to="/">
            OB2
          </Link>
          <div className="navbar-nav ms-auto flex-row gap-3">
            <Link className="nav-link" to="/">
              Публикации
            </Link>
            {isAuthenticated ? (
              <>
                <Link className="nav-link" to="/profile">
                  Профиль
                </Link>
                <span className="navbar-text text-white-50 d-none d-md-inline">
                  {user?.phone}
                </span>
                <button type="button" className="btn btn-outline-light btn-sm" onClick={logout}>
                  Выйти
                </button>
              </>
            ) : (
              <>
                <Link className="nav-link" to="/login">
                  Вход
                </Link>
                <Link className="nav-link" to="/register">
                  Регистрация
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
      <main className="container pb-5">
        <Outlet />
      </main>
    </>
  );
}
