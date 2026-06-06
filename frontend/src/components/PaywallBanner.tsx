import { Link } from "react-router-dom";

/** Баннер paywall: показывается, когда полный текст публикации недоступен (can_view_body=false). */
export default function PaywallBanner() {
  return (
    <div className="alert alert-warning" role="alert">
      <h2 className="h5 alert-heading">Платный контент</h2>
      <p className="mb-2">
        Полный текст доступен после оплаты разовой подписки.
      </p>
      <Link className="btn btn-primary btn-sm" to="/profile">
        Оформить подписку
      </Link>
    </div>
  );
}
