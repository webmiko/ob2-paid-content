import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiJson } from "../api/client";
import type { PaymentSuccessResponse } from "../api/types";
import { useAuth } from "../context/AuthContext";

export default function PaymentSuccessPage() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const { isAuthenticated, refreshProfile } = useAuth();
  const [message, setMessage] = useState("Проверяем оплату…");
  const [success, setSuccess] = useState<boolean | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setMessage("Не указан session_id.");
      setSuccess(false);
      return;
    }
    if (!isAuthenticated) {
      setMessage("Войдите в аккаунт — JWT сохранён в браузере после логина.");
      setSuccess(false);
      return;
    }

    const confirm = async () => {
      try {
        const data = await apiJson<PaymentSuccessResponse>(
          `/api/payments/success/?session_id=${encodeURIComponent(sessionId)}`,
        );
        await refreshProfile();
        if (data.subscription_active) {
          setMessage("Подписка активирована. Платный контент доступен.");
          setSuccess(true);
        } else {
          setMessage("Оплата ещё не подтверждена. Обновите страницу позже.");
          setSuccess(false);
        }
      } catch {
        setMessage("Не удалось подтвердить оплату.");
        setSuccess(false);
      }
    };
    void confirm();
  }, [sessionId, isAuthenticated, refreshProfile]);

  return (
    <section className="text-center py-5">
      <h1 className="mb-3">Оплата</h1>
      <div
        className={`alert ${success ? "alert-success" : success === false ? "alert-warning" : "alert-info"}`}
      >
        {message}
      </div>
      <Link className="btn btn-primary" to="/">
        К публикациям
      </Link>
      {!isAuthenticated && (
        <p className="mt-3">
          <Link to="/login">Войти</Link>, если вы ещё не авторизованы.
        </p>
      )}
    </section>
  );
}
