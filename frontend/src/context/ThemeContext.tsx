import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import {
  msUntilNextTransition,
  readStoredCoords,
  readThemePreference,
  requestBrowserCoords,
  resolveCoords,
  resolveThemeFromPreference,
  THEME_STORAGE_KEY,
  type GeoCoords,
  type ResolvedTheme,
  type ThemePreference,
} from "../theme/solar";

interface ThemeContextValue {
  preference: ThemePreference;
  resolvedTheme: ResolvedTheme;
  coords: GeoCoords;
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
  const [coords, setCoords] = useState<GeoCoords>(() => resolveCoords());
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>(() =>
    resolveThemeFromPreference(readThemePreference(), resolveCoords()),
  );
  const timerRef = useRef<number | null>(null);

  const syncResolved = useCallback(
    (pref: ThemePreference, geo: GeoCoords) => {
      const resolved = resolveThemeFromPreference(pref, geo);
      setResolvedTheme(resolved);
      applyDomTheme(resolved);
    },
    [],
  );

  const scheduleAutoCheck = useCallback(
    (pref: ThemePreference, geo: GeoCoords) => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      if (pref !== "auto") {
        return;
      }
      const delay = Math.max(msUntilNextTransition(new Date(), geo), 30_000);
      timerRef.current = window.setTimeout(() => {
        syncResolved("auto", geo);
        scheduleAutoCheck("auto", geo);
      }, delay);
    },
    [syncResolved],
  );

  const setPreference = useCallback(
    (next: ThemePreference) => {
      localStorage.setItem(THEME_STORAGE_KEY, next);
      setPreferenceState(next);
      syncResolved(next, coords);
      scheduleAutoCheck(next, coords);
    },
    [coords, scheduleAutoCheck, syncResolved],
  );

  const cyclePreference = useCallback(() => {
    setPreference(nextPreference(preference));
  }, [preference, setPreference]);

  useEffect(() => {
    syncResolved(preference, coords);
    scheduleAutoCheck(preference, coords);
    return () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, [coords, preference, scheduleAutoCheck, syncResolved]);

  useEffect(() => {
    if (preference !== "auto") {
      return;
    }
    const interval = window.setInterval(() => {
      syncResolved("auto", coords);
    }, 60_000);
    return () => window.clearInterval(interval);
  }, [coords, preference, syncResolved]);

  useEffect(() => {
    if (readStoredCoords()) {
      return;
    }
    void requestBrowserCoords().then((geo) => {
      if (!geo) {
        return;
      }
      setCoords(geo);
    });
  }, []);

  const value = useMemo(
    () => ({
      preference,
      resolvedTheme,
      coords,
      setPreference,
      cyclePreference,
    }),
    [coords, cyclePreference, preference, resolvedTheme, setPreference],
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
