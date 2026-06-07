import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import PageMeta from "../components/PageMeta";
import PhoneInput from "../components/PhoneInput";
import { useAuth } from "../context/AuthContext";
import type { PhoneCountry } from "../utils/phone";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [country, setCountry] = useState<PhoneCountry>("ru");
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
          <PhoneInput
            id="phone"
            country={country}
            value={phone}
            onCountryChange={setCountry}
            onChange={setPhone}
            required
          />
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
