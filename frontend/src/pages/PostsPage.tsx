import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiJson } from "../api/client";
import type { Paginated, Post } from "../api/types";

export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiJson<Paginated<Post>>("/api/posts/");
        setPosts(data.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  if (loading) {
    return <p className="text-muted">Загрузка публикаций…</p>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <section>
      <h1 className="mb-4">Публикации</h1>
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
              <p className="mb-1 text-muted small">Автор: {post.author_phone}</p>
              {post.can_view_body && post.body ? (
                <p className="mb-0 text-truncate">{post.body}</p>
              ) : (
                <p className="mb-0 text-muted fst-italic">Текст скрыт</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
