import { Link } from "react-router-dom";

export default function PaymentCancelPage() {
  return (
    <section className="auth-wrap text-center">
      <h1 className="page-title">Оплата отменена</h1>
      <div className="card alert-custom alert-warning-custom mb-4">
        Платёж не был завершён. Подписка не активирована.
      </div>
      <div className="d-flex flex-wrap justify-content-center gap-2">
        <Link className="btn-pill" to="/profile">
          В профиль
        </Link>
        <Link className="btn-pill btn-pill-secondary" to="/">
          К публикациям
        </Link>
      </div>
    </section>
  );
}
