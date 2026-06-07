import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import PageMeta from "../components/PageMeta";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
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
      await login(phone, password);
      navigate("/profile");
    } catch (err) {
      setError(err instanceof ApiError ? "Неверный телефон или пароль" : "Ошибка входа");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PageMeta
        title="Вход"
        description="Вход в аккаунт Creavity по номеру телефона."
        path="/login"
        noIndex
      />
      <div className="auth-wrap">
      <h1 className="page-title">
        <i className="fa-solid fa-right-to-bracket" aria-hidden="true" /> Вход
      </h1>
      <form className="card" onSubmit={handleSubmit}>
        {error && <div className="alert-custom alert-danger-custom">{error}</div>}
        <div className="form-group">
          <label htmlFor="phone">Телефон</label>
          <input
            id="phone"
            className="form-control-custom"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+7 900 123-45-67"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Пароль</label>
          <input
            id="password"
            type="password"
            className="form-control-custom"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </div>
        <button type="submit" className="btn-pill" disabled={submitting} style={{ width: "100%" }}>
          {submitting ? "Вход…" : "Войти"}
        </button>
      </form>
      <p className="mt-3">
        Нет аккаунта? <Link className="text-link" to="/register">Регистрация</Link>
      </p>
    </div>
    </>
  );
}
