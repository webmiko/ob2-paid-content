import type { FormEvent } from "react";
import { useState } from "react";
import { Navigate } from "react-router-dom";

import { apiJson } from "../api/client";
import type { PaymentCreateResponse } from "../api/types";
import { useAuth } from "../context/AuthContext";

export default function ProfilePage() {
  const { user, loading, isAuthenticated, refreshProfile } = useAuth();
  const [payError, setPayError] = useState<string | null>(null);
  const [payLoading, setPayLoading] = useState(false);
  const [postTitle, setPostTitle] = useState("");
  const [postBody, setPostBody] = useState("");
  const [postPaid, setPostPaid] = useState(false);
  const [postMessage, setPostMessage] = useState<string | null>(null);

  if (loading) {
    return <p className="text-muted">Загрузка профиля…</p>;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  const handlePay = async () => {
    setPayLoading(true);
    setPayError(null);
    try {
      const data = await apiJson<PaymentCreateResponse>("/api/payments/create/", {
        method: "POST",
      });
      window.location.href = data.payment_url;
    } catch {
      setPayError("Не удалось создать платёж. Попробуйте позже.");
      setPayLoading(false);
    }
  };

  const handleCreatePost = async (event: FormEvent) => {
    event.preventDefault();
    setPostMessage(null);
    try {
      await apiJson("/api/posts/", {
        method: "POST",
        body: JSON.stringify({
          title: postTitle,
          body: postBody,
          is_paid: postPaid,
        }),
      });
      setPostTitle("");
      setPostBody("");
      setPostPaid(false);
      setPostMessage("Публикация создана.");
    } catch {
      setPostMessage("Не удалось создать публикацию.");
    }
  };

  return (
    <section>
      <h1 className="mb-4">Профиль</h1>
      <div className="card mb-4">
        <div className="card-body">
          <p>
            <strong>Телефон:</strong> {user.phone}
          </p>
          <p>
            <strong>Подписка:</strong>{" "}
            {user.subscription_active ? (
              <span className="badge text-bg-success">Активна</span>
            ) : (
              <span className="badge text-bg-secondary">Не активна</span>
            )}
          </p>
          {!user.subscription_active && (
            <>
              {payError && <div className="alert alert-danger">{payError}</div>}
              <button
                type="button"
                className="btn btn-primary"
                onClick={handlePay}
                disabled={payLoading}
              >
                {payLoading ? "Переход к оплате…" : "Оплатить подписку"}
              </button>
            </>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <h2 className="h5">Новая публикация</h2>
          {postMessage && <div className="alert alert-info">{postMessage}</div>}
          <form onSubmit={handleCreatePost}>
            <div className="mb-3">
              <label className="form-label" htmlFor="title">
                Заголовок
              </label>
              <input
                id="title"
                className="form-control"
                value={postTitle}
                onChange={(e) => setPostTitle(e.target.value)}
                required
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="body">
                Текст
              </label>
              <textarea
                id="body"
                className="form-control"
                rows={4}
                value={postBody}
                onChange={(e) => setPostBody(e.target.value)}
                required
              />
            </div>
            <div className="form-check mb-3">
              <input
                id="is_paid"
                type="checkbox"
                className="form-check-input"
                checked={postPaid}
                onChange={(e) => setPostPaid(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="is_paid">
                Платная публикация
              </label>
            </div>
            <button type="submit" className="btn btn-outline-primary">
              Опубликовать
            </button>
          </form>
        </div>
      </div>

      <button type="button" className="btn btn-link mt-3 ps-0" onClick={() => void refreshProfile()}>
        Обновить статус подписки
      </button>
    </section>
  );
}
