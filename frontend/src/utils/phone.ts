/** Маски телефонов RU / BY / KZ и нормализация для API. */

export type PhoneCountry = "ru" | "by" | "kz";

export interface PhoneCountryConfig {
  code: PhoneCountry;
  label: string;
  flag: string;
  placeholder: string;
  dialCode: string;
  totalDigits: number;
}

export const PHONE_COUNTRIES: PhoneCountryConfig[] = [
  {
    code: "ru",
    label: "Россия",
    flag: "🇷🇺",
    placeholder: "+7 (900) 123-45-67",
    dialCode: "7",
    totalDigits: 11,
  },
  {
    code: "kz",
    label: "Казахстан",
    flag: "🇰🇿",
    placeholder: "+7 (771) 123-45-67",
    dialCode: "7",
    totalDigits: 11,
  },
  {
    code: "by",
    label: "Беларусь",
    flag: "🇧🇾",
    placeholder: "+375 (29) 123-45-67",
    dialCode: "375",
    totalDigits: 12,
  },
];

export function phoneCountryConfig(country: PhoneCountry): PhoneCountryConfig {
  return PHONE_COUNTRIES.find((item) => item.code === country) ?? PHONE_COUNTRIES[0]!;
}

export function extractPhoneDigits(value: string): string {
  return value.replace(/\D/g, "");
}

function formatRuKz(digits: string): string {
  let d = digits;
  if (d.startsWith("8")) {
    d = `7${d.slice(1)}`;
  }
  if (!d.startsWith("7")) {
    d = `7${d}`;
  }
  d = d.slice(0, 11);
  const parts = [
    d.slice(0, 1),
    d.slice(1, 4),
    d.slice(4, 7),
    d.slice(7, 9),
    d.slice(9, 11),
  ];
  let out = `+${parts[0]}`;
  if (parts[1]) {
    out += ` (${parts[1]}`;
  }
  if (parts[1]?.length === 3) {
    out += ")";
  }
  if (parts[2]) {
    out += ` ${parts[2]}`;
  }
  if (parts[3]) {
    out += `-${parts[3]}`;
  }
  if (parts[4]) {
    out += `-${parts[4]}`;
  }
  return out;
}

function formatBelarus(digits: string): string {
  let d = digits;
  if (!d.startsWith("375")) {
    d = `375${d}`;
  }
  d = d.slice(0, 12);
  const a = d.slice(3, 5);
  const b = d.slice(5, 8);
  const c = d.slice(8, 10);
  const e = d.slice(10, 12);
  let out = "+375";
  if (a) {
    out += ` (${a}`;
  }
  if (a.length === 2) {
    out += ")";
  }
  if (b) {
    out += ` ${b}`;
  }
  if (c) {
    out += `-${c}`;
  }
  if (e) {
    out += `-${e}`;
  }
  return out;
}

export function formatPhoneInput(value: string, country: PhoneCountry): string {
  const digits = extractPhoneDigits(value);
  if (country === "by") {
    return formatBelarus(digits);
  }
  return formatRuKz(digits);
}

export function isPhoneComplete(value: string, country: PhoneCountry): boolean {
  const digits = extractPhoneDigits(value);
  const cfg = phoneCountryConfig(country);
  return digits.length === cfg.totalDigits;
}
