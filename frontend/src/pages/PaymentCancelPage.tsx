import { Link } from "react-router-dom";

export default function PaymentCancelPage() {
  return (
    <section className="text-center py-5">
      <h1 className="mb-3">Оплата отменена</h1>
      <div className="alert alert-secondary">
        Платёж не был завершён. Подписка не активирована.
      </div>
      <Link className="btn btn-primary me-2" to="/profile">
        В профиль
      </Link>
      <Link className="btn btn-outline-secondary" to="/">
        К публикациям
      </Link>
    </section>
  );
}
