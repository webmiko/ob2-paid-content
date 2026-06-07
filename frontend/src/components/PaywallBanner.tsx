import { Link } from "react-router-dom";

/** Баннер paywall: показывается, когда полный текст публикации недоступен (can_view_body=false). */
export default function PaywallBanner() {
  return (
    <div className="lock-overlay" role="alert">
      <h2>
        <i className="fa-solid fa-lock" aria-hidden="true" /> Платный контент
      </h2>
      <p className="mb-3">Полный текст доступен после оплаты разовой подписки.</p>
      <Link className="btn-pill btn-sm-pill" to="/profile">
        Оформить подписку
      </Link>
    </div>
  );
}
