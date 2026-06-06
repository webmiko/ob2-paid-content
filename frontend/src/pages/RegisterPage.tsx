import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await register(phone, password, displayName);
      navigate("/profile");
    } catch (err) {
      if (err instanceof ApiError) {
        const displayNameErrors = err.body.display_name;
        const phoneErrors = err.body.phone;
        setError(
          typeof displayNameErrors === "string"
            ? displayNameErrors
            : Array.isArray(displayNameErrors)
              ? String(displayNameErrors[0])
              : typeof phoneErrors === "string"
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
    <div className="auth-wrap">
      <h1 className="page-title">
        <i className="fa-solid fa-user-plus" aria-hidden="true" /> Регистрация
      </h1>
      <form className="card" onSubmit={handleSubmit}>
        {error && <div className="alert-custom alert-danger-custom">{error}</div>}
        <div className="form-group">
          <label htmlFor="display_name">Никнейм</label>
          <input
            id="display_name"
            className="form-control-custom"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Как вас видят на платформе"
            required
            minLength={2}
            maxLength={80}
          />
        </div>
        <div className="form-group">
          <label htmlFor="phone">Телефон для входа</label>
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
          {submitting ? "Регистрация…" : "Зарегистрироваться"}
        </button>
      </form>
      <p className="mt-3">
        Уже есть аккаунт? <Link className="text-link" to="/login">Вход</Link>
      </p>
    </div>
  );
}
