import type { FormEvent } from "react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiJson } from "../api/client";
import type { Comment, Paginated } from "../api/types";
import { useAuth } from "../context/AuthContext";
import { formatPostDate } from "../utils/avatar";
import "../styles/deferred/comments.css";

function apiPathFromNext(next: string | null): string | null {
  if (!next) {
    return null;
  }
  try {
    const parsed = new URL(next, window.location.origin);
    return `${parsed.pathname}${parsed.search}`;
  } catch {
    return next.startsWith("/") ? next : null;
  }
}

interface PostCommentsProps {
  postId: number;
  canAccess: boolean;
  initialCount?: number;
}

export default function PostComments({ postId, canAccess, initialCount = 0 }: PostCommentsProps) {
  const { isAuthenticated } = useAuth();
  const [comments, setComments] = useState<Comment[]>([]);
  const [totalCount, setTotalCount] = useState(initialCount);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const loadComments = useCallback(async (pageUrl?: string, append = false) => {
    if (!canAccess) {
      setComments([]);
      setLoading(false);
      return;
    }
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }
    setError(null);
    try {
      const url = pageUrl ?? `/api/posts/${postId}/comments/`;
      const data = await apiJson<Paginated<Comment>>(url);
      setComments((prev) => (append ? [...prev, ...data.results] : data.results));
      setTotalCount(data.count);
      setNextPage(data.next);
    } catch {
      setError("Не удалось загрузить комментарии.");
      if (!append) {
        setComments([]);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [canAccess, postId]);

  useEffect(() => {
    void loadComments();
  }, [loadComments]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!text.trim()) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const created = await apiJson<Comment>(`/api/posts/${postId}/comments/`, {
        method: "POST",
        body: JSON.stringify({ text: text.trim() }),
      });
      setComments((prev) => [...prev, created]);
      setTotalCount((prev) => prev + 1);
      setText("");
    } catch {
      setError("Не удалось отправить комментарий. Проверьте соединение и попробуйте снова.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (commentId: number) => {
    setDeletingId(commentId);
    setError(null);
    try {
      await apiJson(`/api/posts/${postId}/comments/${commentId}/`, { method: "DELETE" });
      setComments((prev) => prev.filter((item) => item.id !== commentId));
      setTotalCount((prev) => Math.max(0, prev - 1));
    } catch {
      setError("Не удалось удалить комментарий.");
    } finally {
      setDeletingId(null);
    }
  };

  if (!canAccess) {
    return (
      <section className="comments-section comments-locked card">
        <h2 className="section-title">
          <i className="fa-solid fa-comments" aria-hidden="true" /> Комментарии
        </h2>
        <p className="hint-text">Комментарии откроются вместе с текстом и видео публикации.</p>
        <Link className="btn-pill btn-sm-pill" to="/profile">
          Оформить подписку
        </Link>
      </section>
    );
  }

  return (
    <section className="comments-section card">
      <h2 className="section-title">
        <i className="fa-solid fa-comments" aria-hidden="true" /> Комментарии
        <span className="comments-count">{totalCount}</span>
      </h2>
      {error && (
        <div className="alert-custom alert-warning-custom">
          {error}{" "}
          <button type="button" className="text-link-btn" onClick={() => void loadComments()}>
            Повторить
          </button>
        </div>
      )}
      {loading ? (
        <p className="loading-text">Загрузка комментариев…</p>
      ) : comments.length === 0 ? (
        <p className="hint-text">Пока нет комментариев — будьте первым.</p>
      ) : (
        <ul className="comments-list">
          {comments.map((comment) => (
            <li key={comment.id} className="comment-item">
              <div className="comment-meta">
                <strong>{comment.author_label}</strong>
                <span>{formatPostDate(comment.created_at)}</span>
              </div>
              <p>{comment.text}</p>
              {comment.can_delete && (
                <button
                  type="button"
                  className="btn-pill btn-pill-outline btn-sm-pill comment-delete-btn"
                  disabled={deletingId === comment.id}
                  onClick={() => void handleDelete(comment.id)}
                >
                  {deletingId === comment.id ? "Удаление…" : "Удалить"}
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      {nextPage && (
        <button
          type="button"
          className="btn-pill btn-pill-secondary btn-sm-pill"
          disabled={loadingMore}
          onClick={() => {
            const path = apiPathFromNext(nextPage);
            if (path) {
              void loadComments(path, true);
            }
          }}
        >
          {loadingMore ? "Загрузка…" : "Показать ещё"}
        </button>
      )}
      {isAuthenticated ? (
        <form className="comment-form" onSubmit={handleSubmit}>
          <textarea
            rows={3}
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Напишите комментарий…"
            maxLength={2000}
            required
          />
          <button type="submit" className="btn-pill btn-sm-pill" disabled={submitting}>
            {submitting ? "Отправка…" : "Отправить"}
          </button>
        </form>
      ) : (
        <p className="hint-text">
          <Link className="text-link" to="/login">
            Войдите
          </Link>
          , чтобы оставить комментарий.
        </p>
      )}
    </section>
  );
}
