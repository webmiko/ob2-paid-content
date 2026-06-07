import type { ChangeEvent } from "react";

import {
  formatPhoneInput,
  PHONE_COUNTRIES,
  type PhoneCountry,
} from "../utils/phone";

interface PhoneInputProps {
  id: string;
  country: PhoneCountry;
  value: string;
  onCountryChange: (country: PhoneCountry) => void;
  onChange: (formatted: string) => void;
  required?: boolean;
  label?: string;
}

export default function PhoneInput({
  id,
  country,
  value,
  onCountryChange,
  onChange,
  required = false,
  label = "Телефон",
}: PhoneInputProps) {
  const cfg = PHONE_COUNTRIES.find((item) => item.code === country)!;

  const handlePhoneChange = (event: ChangeEvent<HTMLInputElement>) => {
    onChange(formatPhoneInput(event.target.value, country));
  };

  const handleCountryChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const next = event.target.value as PhoneCountry;
    onCountryChange(next);
    onChange(formatPhoneInput("", next));
  };

  return (
    <div className="form-group">
      <label htmlFor={id}>{label}</label>
      <div className="phone-input-row">
        <select
          className="phone-country-select"
          value={country}
          onChange={handleCountryChange}
          aria-label="Страна номера"
        >
          {PHONE_COUNTRIES.map((item) => (
            <option key={item.code} value={item.code}>
              {item.flag} {item.label}
            </option>
          ))}
        </select>
        <input
          id={id}
          type="tel"
          inputMode="tel"
          autoComplete="tel"
          className="form-control-custom phone-input-field"
          value={value}
          onChange={handlePhoneChange}
          placeholder={cfg.placeholder}
          required={required}
        />
      </div>
    </div>
  );
}
