import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiJson, hasRefreshToken } from "../api/client";
import type { PaymentSuccessResponse } from "../api/types";
import { useAuth } from "../context/AuthContext";

export default function PaymentSuccessPage() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const { loading, refreshProfile } = useAuth();
  const [message, setMessage] = useState("Проверяем оплату…");
  const [success, setSuccess] = useState<boolean | null>(null);
  const [needsLogin, setNeedsLogin] = useState(false);

  useEffect(() => {
    if (loading) {
      return;
    }
    if (!sessionId) {
      setMessage("Не указан session_id.");
      setSuccess(false);
      return;
    }
    if (!hasRefreshToken()) {
      setMessage("Войдите в аккаунт, чтобы активировать подписку.");
      setSuccess(false);
      setNeedsLogin(true);
      return;
    }

    const confirm = async () => {
      try {
        const data = await apiJson<PaymentSuccessResponse>("/api/payments/success/", {
          method: "POST",
          body: JSON.stringify({ session_id: sessionId }),
        });
        await refreshProfile();
        if (data.subscription_active) {
          setMessage("Подписка активирована. Платный контент доступен.");
          setSuccess(true);
          setNeedsLogin(false);
        } else {
          setMessage("Оплата ещё не подтверждена. Обновите страницу или проверьте статус в профиле.");
          setSuccess(false);
        }
      } catch {
        setMessage("Не удалось подтвердить оплату.");
        setSuccess(false);
      }
    };
    void confirm();
  }, [sessionId, loading, refreshProfile]);

  return (
    <section className="text-center py-5">
      <h1 className="mb-3">Оплата</h1>
      <div
        className={`alert ${success ? "alert-success" : success === false ? "alert-warning" : "alert-info"}`}
      >
        {loading ? "Загрузка…" : message}
      </div>
      <Link className="btn btn-primary" to="/">
        К публикациям
      </Link>
      {needsLogin && (
        <p className="mt-3">
          <Link to="/login">Войти</Link>, если вы ещё не авторизованы.
        </p>
      )}
    </section>
  );
}
