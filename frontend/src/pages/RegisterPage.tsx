import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError, apiJson } from "../api/client";
import PageMeta from "../components/PageMeta";
import PhoneInput from "../components/PhoneInput";
import { useAuth } from "../context/AuthContext";
import { isPhoneComplete, type PhoneCountry } from "../utils/phone";

interface SendCodeResponse {
  detail: string;
  simulation_code?: string;
}

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState("");
  const [country, setCountry] = useState<PhoneCountry>("ru");
  const [phone, setPhone] = useState("");
  const [smsCode, setSmsCode] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [simulationCode, setSimulationCode] = useState<string | null>(null);
  const [codeSent, setCodeSent] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSendCode = async () => {
    if (!isPhoneComplete(phone, country)) {
      setError("Введите номер телефона полностью.");
      return;
    }
    setSendingCode(true);
    setError(null);
    setInfo(null);
    setSimulationCode(null);
    try {
      const response = await apiJson<SendCodeResponse>("/api/users/phone/send-code/", {
        method: "POST",
        body: JSON.stringify({ phone, country }),
      });
      setCodeSent(true);
      setInfo(response.detail);
      if (response.simulation_code) {
        setSimulationCode(response.simulation_code);
        setSmsCode(response.simulation_code);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        const phoneErrors = err.body.phone;
        setError(
          typeof phoneErrors === "string"
            ? phoneErrors
            : Array.isArray(phoneErrors)
              ? String(phoneErrors[0])
              : "Не удалось отправить код.",
        );
      } else {
        setError("Не удалось отправить код.");
      }
    } finally {
      setSendingCode(false);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!codeSent) {
      setError("Сначала получите код подтверждения по SMS.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await register(phone, password, displayName, country, smsCode);
      navigate("/profile");
    } catch (err) {
      if (err instanceof ApiError) {
        const displayNameErrors = err.body.display_name;
        const phoneErrors = err.body.phone;
        const smsErrors = err.body.sms_code;
        setError(
          typeof displayNameErrors === "string"
            ? displayNameErrors
            : Array.isArray(displayNameErrors)
              ? String(displayNameErrors[0])
              : typeof smsErrors === "string"
                ? smsErrors
                : Array.isArray(smsErrors)
                  ? String(smsErrors[0])
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
    <>
      <PageMeta
        title="Регистрация"
        description="Создайте аккаунт Creavity и получите доступ к платному контенту по подписке платформы."
        path="/register"
        noIndex
      />
      <div className="auth-wrap">
        <h1 className="page-title">
          <i className="fa-solid fa-user-plus" aria-hidden="true" /> Регистрация
        </h1>
        <form className="card" onSubmit={handleSubmit}>
          {error && <div className="alert-custom alert-danger-custom">{error}</div>}
          {info && <div className="alert-custom alert-info-custom">{info}</div>}
          {simulationCode && (
            <div className="alert-custom alert-warning-custom sms-demo-hint">
              Демо-режим: код подтверждения — <strong>{simulationCode}</strong>
            </div>
          )}
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
          <PhoneInput
            id="phone"
            label="Телефон для входа"
            country={country}
            value={phone}
            onCountryChange={(next) => {
              setCountry(next);
              setCodeSent(false);
              setSmsCode("");
              setSimulationCode(null);
            }}
            onChange={(formatted) => {
              setPhone(formatted);
              setCodeSent(false);
            }}
            required
          />
          <div className="form-group">
            <button
              type="button"
              className="btn-pill btn-pill-secondary"
              style={{ width: "100%" }}
              disabled={sendingCode || !isPhoneComplete(phone, country)}
              onClick={() => void handleSendCode()}
            >
              {sendingCode ? "Отправка…" : codeSent ? "Отправить код снова" : "Получить код по SMS"}
            </button>
          </div>
          {codeSent && (
            <div className="form-group">
              <label htmlFor="sms_code">Код из SMS</label>
              <input
                id="sms_code"
                className="form-control-custom sms-code-input"
                value={smsCode}
                onChange={(e) => setSmsCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                placeholder="6 цифр"
                inputMode="numeric"
                autoComplete="one-time-code"
                required
                minLength={4}
                maxLength={6}
              />
            </div>
          )}
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
          <button
            type="submit"
            className="btn-pill"
            disabled={submitting || !codeSent}
            style={{ width: "100%" }}
          >
            {submitting ? "Регистрация…" : "Зарегистрироваться"}
          </button>
        </form>
        <p className="mt-3">
          Уже есть аккаунт? <Link className="text-link" to="/login">Вход</Link>
        </p>
      </div>
    </>
  );
}
