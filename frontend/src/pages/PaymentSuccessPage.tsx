import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiJson, hasRefreshToken } from "../api/client";
import type { PaymentSuccessResponse } from "../api/types";
import PageMeta from "../components/PageMeta";
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

  const alertClass =
    success === true
      ? "alert-success-custom"
      : success === false
        ? "alert-warning-custom"
        : "alert-info-custom";

  return (
    <>
      <PageMeta
        title="Оплата"
        description="Подтверждение оплаты подписки Creavity."
        path="/payment/success"
        noIndex
      />
      <section className="auth-wrap text-center">
      <h1 className="page-title">Оплата</h1>
      <div className={`card alert-custom ${alertClass}`}>
        {loading ? "Загрузка…" : message}
      </div>
      <Link className="btn-pill" to="/">
        К публикациям
      </Link>
      {needsLogin && (
        <p className="mt-3">
          <Link className="text-link" to="/login">
            Войти
          </Link>
          , если вы ещё не авторизованы.
        </p>
      )}
    </section>
    </>
  );
}
