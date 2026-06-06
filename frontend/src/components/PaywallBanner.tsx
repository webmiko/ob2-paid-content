import { Link } from "react-router-dom";

/** CTA при can_view_body=false — paywall только по данным API. */
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
