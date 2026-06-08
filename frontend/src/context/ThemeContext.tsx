import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  readThemePreference,
  resolveThemeFromPreference,
  subscribeSystemTheme,
  THEME_STORAGE_KEY,
  type ResolvedTheme,
  type ThemePreference,
} from "../theme/theme";

interface ThemeContextValue {
  preference: ThemePreference;
  resolvedTheme: ResolvedTheme;
  setPreference: (next: ThemePreference) => void;
  cyclePreference: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const META_THEME: Record<ResolvedTheme, string> = {
  light: "#6366f1",
  dark: "#1e293b",
};

function applyDomTheme(resolved: ResolvedTheme): void {
  document.documentElement.dataset.theme = resolved;
  document.documentElement.dataset.bsTheme = resolved;
  document.documentElement.style.colorScheme = resolved;

  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) {
    meta.setAttribute("content", META_THEME[resolved]);
  }
}

function nextPreference(current: ThemePreference): ThemePreference {
  if (current === "auto") {
    return "light";
  }
  if (current === "light") {
    return "dark";
  }
  return "auto";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [preference, setPreferenceState] = useState<ThemePreference>(() => readThemePreference());
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>(() =>
    resolveThemeFromPreference(readThemePreference()),
  );

  const syncResolved = useCallback((pref: ThemePreference) => {
    const resolved = resolveThemeFromPreference(pref);
    setResolvedTheme(resolved);
    applyDomTheme(resolved);
  }, []);

  const setPreference = useCallback(
    (next: ThemePreference) => {
      localStorage.setItem(THEME_STORAGE_KEY, next);
      setPreferenceState(next);
      syncResolved(next);
    },
    [syncResolved],
  );

  const cyclePreference = useCallback(() => {
    setPreference(nextPreference(preference));
  }, [preference, setPreference]);

  useEffect(() => {
    syncResolved(preference);
  }, [preference, syncResolved]);

  useEffect(() => {
    if (preference !== "auto") {
      return;
    }
    return subscribeSystemTheme(() => syncResolved("auto"));
  }, [preference, syncResolved]);

  const value = useMemo(
    () => ({
      preference,
      resolvedTheme,
      setPreference,
      cyclePreference,
    }),
    [cyclePreference, preference, resolvedTheme, setPreference],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
}
