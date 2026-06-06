import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { ApiError, apiJson, clearTokens, hasRefreshToken, logoutApi, setTokens } from "../api/client";
import type { TokenPair, UserProfile } from "../api/types";

interface AuthContextValue {
  user: UserProfile | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (phone: string, password: string) => Promise<void>;
  register: (phone: string, password: string, displayName: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

async function obtainTokens(phone: string, password: string): Promise<TokenPair> {
  return apiJson<TokenPair>("/api/token/", {
    method: "POST",
    body: JSON.stringify({ phone, password }),
  });
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = useCallback(async () => {
    if (!hasRefreshToken()) {
      setUser(null);
      return;
    }
    try {
      const profile = await apiJson<UserProfile>("/api/users/me/");
      setUser(profile);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearTokens();
        setUser(null);
      }
    }
  }, []);

  useEffect(() => {
    const bootstrap = async () => {
      if (!hasRefreshToken()) {
        setLoading(false);
        return;
      }
      await refreshProfile();
      setLoading(false);
    };
    void bootstrap();
  }, [refreshProfile]);

  const login = useCallback(async (phone: string, password: string) => {
    const tokens = await obtainTokens(phone, password);
    setTokens(tokens.access, tokens.refresh);
    const profile = await apiJson<UserProfile>("/api/users/me/");
    setUser(profile);
  }, []);

  const register = useCallback(async (phone: string, password: string, displayName: string) => {
    await apiJson("/api/users/register/", {
      method: "POST",
      body: JSON.stringify({ phone, password, display_name: displayName.trim() }),
    });
    await login(phone, password);
  }, [login]);

  const logout = useCallback(async () => {
    await logoutApi();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshProfile,
    }),
    [user, loading, login, register, logout, refreshProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
