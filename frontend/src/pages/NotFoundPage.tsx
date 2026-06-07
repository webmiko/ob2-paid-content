import { Link, useLocation } from "react-router-dom";

import PageMeta from "../components/PageMeta";

export default function NotFoundPage() {
  const { pathname } = useLocation();

  return (
    <>
      <PageMeta
        title="Страница не найдена"
        description="Запрошенная страница не существует на Creavity."
        path={pathname}
        noIndex
      />
      <section className="card not-found-card">
        <h1 className="page-title">404 — страница не найдена</h1>
        <p className="page-subtitle">
          Такой страницы нет. Перейдите в ленту или откройте каталог авторов и тем.
        </p>
        <p className="mb-0">
          <Link className="text-link" to="/">
            На главную
          </Link>
          {" · "}
          <Link className="text-link" to="/explore">
            К каталогу
          </Link>
        </p>
      </section>
    </>
  );
}
