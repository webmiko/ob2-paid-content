import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiJson } from "../api/client";
import type { Post } from "../api/types";
import PaywallBanner from "../components/PaywallBanner";

export default function PostDetailPage() {
  const { id } = useParams();
  const [post, setPost] = useState<Post | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) {
      return;
    }
    const load = async () => {
      try {
        const data = await apiJson<Post>(`/api/posts/${id}/`);
        setPost(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось загрузить публикацию.");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [id]);

  if (loading) {
    return <p className="text-muted">Загрузка…</p>;
  }

  if (error || !post) {
    return (
      <div className="alert alert-danger">
        {error ?? "Публикация не найдена"}{" "}
        <Link to="/">На главную</Link>
      </div>
    );
  }

  return (
    <article>
      <Link to="/" className="btn btn-link ps-0">
        ← К списку
      </Link>
      <h1 className="mb-2">{post.title}</h1>
      <p className="text-muted">
        Автор #{post.author_id}
        {post.is_paid && (
          <span className="badge text-bg-warning ms-2">Платная</span>
        )}
      </p>
      {post.can_view_body && post.body ? (
        <div className="card">
          <div className="card-body">
            <p className="mb-0" style={{ whiteSpace: "pre-wrap" }}>
              {post.body}
            </p>
          </div>
        </div>
      ) : (
        <PaywallBanner />
      )}
    </article>
  );
}
