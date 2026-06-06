import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiJson } from "../api/client";
import type { Paginated, Post } from "../api/types";

function apiPathFromPaginatedUrl(next: string | null): string | null {
  if (!next) {
    return null;
  }
  try {
    const url = new URL(next, window.location.origin);
    return `${url.pathname}${url.search}`;
  } catch {
    return next;
  }
}

export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [nextPath, setNextPath] = useState<string | null>(null);

  const loadPage = useCallback(async (path: string, append: boolean) => {
    const data = await apiJson<Paginated<Post>>(path);
    setPosts((prev) => (append ? [...prev, ...data.results] : data.results));
    setNextPath(apiPathFromPaginatedUrl(data.next));
  }, []);

  useEffect(() => {
    const load = async () => {
      try {
        await loadPage("/api/posts/", false);
      } catch {
        setError("Не удалось загрузить публикации.");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [loadPage]);

  const loadMore = async () => {
    if (!nextPath) {
      return;
    }
    setLoadingMore(true);
    setError(null);
    try {
      await loadPage(nextPath, true);
    } catch {
      setError("Не удалось загрузить следующую страницу.");
    } finally {
      setLoadingMore(false);
    }
  };

  if (loading) {
    return <p className="text-muted">Загрузка публикаций…</p>;
  }

  if (error && posts.length === 0) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <section>
      <h1 className="mb-4">Публикации</h1>
      {error && <div className="alert alert-warning">{error}</div>}
      {posts.length === 0 ? (
        <p className="text-muted">Пока нет публикаций.</p>
      ) : (
        <div className="list-group">
          {posts.map((post) => (
            <Link
              key={post.id}
              to={`/posts/${post.id}`}
              className="list-group-item list-group-item-action"
            >
              <div className="d-flex w-100 justify-content-between">
                <h2 className="h5 mb-1">{post.title}</h2>
                {post.is_paid ? (
                  <span className="badge text-bg-warning">Платная</span>
                ) : (
                  <span className="badge text-bg-success">Бесплатная</span>
                )}
              </div>
              <p className="mb-1 text-muted small">Автор #{post.author_id}</p>
              {post.can_view_body && post.body ? (
                <p className="mb-0 text-truncate">{post.body}</p>
              ) : (
                <p className="mb-0 text-muted fst-italic">Текст скрыт</p>
              )}
            </Link>
          ))}
        </div>
      )}
      {nextPath && (
        <button
          type="button"
          className="btn btn-outline-primary mt-3"
          onClick={() => void loadMore()}
          disabled={loadingMore}
        >
          {loadingMore ? "Загрузка…" : "Показать ещё"}
        </button>
      )}
    </section>
  );
}
