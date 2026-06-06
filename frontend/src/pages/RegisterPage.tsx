import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await register(phone, password);
      navigate("/profile");
    } catch (err) {
      if (err instanceof ApiError) {
        const phoneErrors = err.body.phone;
        setError(
          typeof phoneErrors === "string"
            ? phoneErrors
            : Array.isArray(phoneErrors)
              ? String(phoneErrors[0])
              : "Не удалось зарегистрироваться",
        );
      } else {
        setError("Ошибка регистрации");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-6 col-lg-5">
        <h1 className="mb-4">Регистрация</h1>
        <form className="card card-body" onSubmit={handleSubmit}>
          {error && <div className="alert alert-danger">{error}</div>}
          <div className="mb-3">
            <label className="form-label" htmlFor="phone">
              Телефон
            </label>
            <input
              id="phone"
              className="form-control"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+7 900 123-45-67"
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="password">
              Пароль
            </label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>
          <button type="submit" className="btn btn-primary w-100" disabled={submitting}>
            {submitting ? "Регистрация…" : "Зарегистрироваться"}
          </button>
        </form>
        <p className="mt-3">
          Уже есть аккаунт? <Link to="/login">Вход</Link>
        </p>
      </div>
    </div>
  );
}
