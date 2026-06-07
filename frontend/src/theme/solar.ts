/** Расчёт рассвета и заката (алгоритм SunCalc, MIT). */

export interface GeoCoords {
  lat: number;
  lng: number;
}

export interface SunTimes {
  sunrise: Date;
  sunset: Date;
}

export const DEFAULT_COORDS: GeoCoords = { lat: 55.7558, lng: 37.6174 };

export type ThemePreference = "light" | "dark" | "auto";
export type ResolvedTheme = "light" | "dark";

export const THEME_STORAGE_KEY = "creavity-theme";
export const COORDS_STORAGE_KEY = "creavity-coords";

const PI = Math.PI;
const RAD = PI / 180;
const DAY_MS = 86_400_000;
const J1970 = 2440588;
const J2000 = 2451545;
const ECLIPTIC_OBLIQUITY = RAD * 23.4397;

function toJulian(date: Date): number {
  return date.valueOf() / DAY_MS - 0.5 + J1970;
}

function fromJulian(j: number): Date {
  return new Date((j + 0.5 - J1970) * DAY_MS);
}

function eclipticLongitude(m: number): number {
  const c = RAD * (1.9148 * Math.sin(m) + 0.02 * Math.sin(2 * m) + 0.0003 * Math.sin(3 * m));
  const p = RAD * 102.9372;
  return m + c + p + PI;
}

function declination(l: number): number {
  return Math.asin(Math.sin(l) * Math.sin(ECLIPTIC_OBLIQUITY));
}

function hourAngle(h: number, phi: number, d: number): number {
  return Math.acos((Math.sin(h) - Math.sin(phi) * Math.sin(d)) / (Math.cos(phi) * Math.cos(d)));
}

function siderealTime(d: number, lw: number): number {
  return RAD * (280.16 + 0.9856474 * d) - lw;
}

function getSetJ(
  h: number,
  lw: number,
  phi: number,
  dec: number,
  n: number,
  m: number,
  rise: boolean,
): number {
  const w = hourAngle(h, phi, dec);
  const a = siderealTime(n, lw) + (rise ? -w : w);
  return J2000 + n + 0.0053 * Math.sin(m) - 0.0069 * Math.sin(2 * a);
}

function sunTimesForDate(date: Date, lat: number, lng: number): SunTimes {
  const lw = RAD * -lng;
  const phi = RAD * lat;
  const d = toJulian(date) - J2000;
  const n = Math.round(d - 0.0009 - lw / (2 * PI));
  const m = RAD * (357.5291 + 0.98560028 * n);
  const dec = declination(eclipticLongitude(m));
  const h = RAD * -0.833;

  return {
    sunrise: fromJulian(getSetJ(h, lw, phi, dec, n, m, true)),
    sunset: fromJulian(getSetJ(h, lw, phi, dec, n, m, false)),
  };
}

export function getSunTimes(date: Date, coords: GeoCoords): SunTimes {
  const day = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  return sunTimesForDate(day, coords.lat, coords.lng);
}

export function isDaytime(date: Date, coords: GeoCoords): boolean {
  const { sunrise, sunset } = getSunTimes(date, coords);
  const t = date.getTime();
  return t >= sunrise.getTime() && t < sunset.getTime();
}

export function msUntilNextTransition(date: Date, coords: GeoCoords): number {
  const { sunrise, sunset } = getSunTimes(date, coords);
  const t = date.getTime();
  if (t < sunrise.getTime()) {
    return sunrise.getTime() - t;
  }
  if (t < sunset.getTime()) {
    return sunset.getTime() - t;
  }
  const tomorrow = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1);
  return getSunTimes(tomorrow, coords).sunrise.getTime() - t;
}

export function readStoredCoords(): GeoCoords | null {
  try {
    const raw = localStorage.getItem(COORDS_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as GeoCoords;
    if (typeof parsed.lat === "number" && typeof parsed.lng === "number") {
      return parsed;
    }
  } catch {
    return null;
  }
  return null;
}

export function storeCoords(coords: GeoCoords): void {
  localStorage.setItem(COORDS_STORAGE_KEY, JSON.stringify(coords));
}

export function resolveCoords(): GeoCoords {
  return readStoredCoords() ?? DEFAULT_COORDS;
}

/** Geolocation доступна только в secure context (HTTPS, localhost). */
export function canUseGeolocation(): boolean {
  return (
    typeof window !== "undefined" &&
    window.isSecureContext &&
    typeof navigator !== "undefined" &&
    Boolean(navigator.geolocation)
  );
}

export function requestBrowserCoords(): Promise<GeoCoords | null> {
  if (!canUseGeolocation()) {
    return Promise.resolve(null);
  }
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        storeCoords(coords);
        resolve(coords);
      },
      () => resolve(null),
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 86_400_000 },
    );
  });
}

export function readThemePreference(): ThemePreference {
  const raw = localStorage.getItem(THEME_STORAGE_KEY);
  if (raw === "light" || raw === "dark" || raw === "auto") {
    return raw;
  }
  return "auto";
}

export function resolveThemeFromPreference(
  preference: ThemePreference,
  coords: GeoCoords,
  now = new Date(),
): ResolvedTheme {
  if (preference === "light") {
    return "light";
  }
  if (preference === "dark") {
    return "dark";
  }
  return isDaytime(now, coords) ? "light" : "dark";
}
