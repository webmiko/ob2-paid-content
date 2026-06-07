import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";

import { ApiError, apiJson, getRefreshToken } from "../api/client";
import { useAuth } from "../context/AuthContext";

interface DeleteAccountSectionProps {
  phone: string;
}

export default function DeleteAccountSection({ phone }: DeleteAccountSectionProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) {
      return;
    }
    const previousOverflow = document.body.style.overflow;
    document.body.classList.add("modal-open");
    document.body.style.overflow = "hidden";
    return () => {
      document.body.classList.remove("modal-open");
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  const resetModal = () => {
    setOpen(false);
    setPassword("");
    setConfirmed(false);
    setError(null);
  };

  const handleDelete = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!confirmed) {
      setError("Отметьте галочку, что понимаете последствия удаления.");
      return;
    }
    if (!password.trim()) {
      setError("Введите пароль для подтверждения.");
      return;
    }

    setSubmitting(true);
    try {
      const refresh = getRefreshToken();
      await apiJson("/api/users/me/", {
        method: "DELETE",
        body: JSON.stringify({
          password,
          confirm: true,
          ...(refresh ? { refresh } : {}),
        }),
      });
      resetModal();
      await logout();
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.body.password) {
        setError(String(err.body.password));
      } else if (err instanceof ApiError && err.body.confirm) {
        setError(String(err.body.confirm));
      } else {
        setError(err instanceof Error ? err.message : "Не удалось удалить профиль.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const modal =
    open &&
    createPortal(
      <div className="modal-backdrop" role="presentation" onClick={resetModal}>
        <div
          className="modal-dialog card"
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-account-title"
          onClick={(event) => event.stopPropagation()}
        >
          <h2 id="delete-account-title" className="section-title">
            Подтверждение удаления
          </h2>
          <p>
            Аккаунт <strong>{phone}</strong> и все связанные материалы будут удалены без возможности
            восстановления.
          </p>
          {error && <div className="alert-custom alert-danger-custom">{error}</div>}
          <form onSubmit={handleDelete}>
            <div className="form-check-custom">
              <input
                id="delete_confirm"
                type="checkbox"
                checked={confirmed}
                onChange={(event) => setConfirmed(event.target.checked)}
              />
              <label htmlFor="delete_confirm">Я понимаю, что удаление необратимо</label>
            </div>
            <div className="form-group">
              <label htmlFor="delete_password">Пароль для подтверждения</label>
              <input
                id="delete_password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                onInput={(event) => setPassword(event.currentTarget.value)}
                autoComplete="current-password"
                placeholder="Текущий пароль от входа"
              />
            </div>
            <p className="hint-text delete-modal-hint">
              Для удаления отметьте галочку и введите пароль, затем нажмите красную кнопку.
            </p>
            <div className="modal-actions">
              <button type="submit" className="btn-pill btn-pill-danger btn-sm-pill" disabled={submitting}>
                {submitting ? "Удаление…" : "Удалить навсегда"}
              </button>
              <button type="button" className="btn-pill btn-pill-outline btn-sm-pill" onClick={resetModal}>
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>,
      document.body,
    );

  return (
    <>
      <div className="card profile-danger-zone">
        <h2 className="section-title">
          <i className="fa-solid fa-triangle-exclamation" aria-hidden="true" /> Удаление профиля
        </h2>
        <p className="hint-text">
          Будут безвозвратно удалены аккаунт, публикации, комментарии и данные подписки.
        </p>
        <button
          type="button"
          className="btn-pill btn-pill-danger btn-sm-pill"
          onClick={() => {
            setError(null);
            setOpen(true);
          }}
        >
          Удалить профиль…
        </button>
      </div>
      {modal}
    </>
  );
}
