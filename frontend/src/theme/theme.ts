/** Тема: светлая / тёмная / авто по настройке устройства (prefers-color-scheme). */

export type ThemePreference = "light" | "dark" | "auto";
export type ResolvedTheme = "light" | "dark";

export const THEME_STORAGE_KEY = "creavity-theme";

const DARK_MEDIA = "(prefers-color-scheme: dark)";

export function getSystemTheme(): ResolvedTheme {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return "light";
  }
  return window.matchMedia(DARK_MEDIA).matches ? "dark" : "light";
}

export function readThemePreference(): ThemePreference {
  const raw = localStorage.getItem(THEME_STORAGE_KEY);
  if (raw === "light" || raw === "dark" || raw === "auto") {
    return raw;
  }
  return "auto";
}

export function resolveThemeFromPreference(preference: ThemePreference): ResolvedTheme {
  if (preference === "light") {
    return "light";
  }
  if (preference === "dark") {
    return "dark";
  }
  return getSystemTheme();
}

export function subscribeSystemTheme(onChange: (theme: ResolvedTheme) => void): () => void {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return () => {};
  }
  const media = window.matchMedia(DARK_MEDIA);
  const handler = () => onChange(getSystemTheme());
  media.addEventListener("change", handler);
  return () => media.removeEventListener("change", handler);
}
