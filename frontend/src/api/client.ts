/** HTTP-клиент с JWT: access в memory, refresh в localStorage. */

import type { ApiErrorBody } from "./types";

const REFRESH_STORAGE_KEY = "ob2_refresh_token";

let accessToken: string | null = null;
let refreshInFlight: Promise<string | null> | null = null;

export class ApiError extends Error {
  status: number;
  body: ApiErrorBody;

  constructor(status: number, body: ApiErrorBody, message?: string) {
    super(message ?? body.detail ?? `HTTP ${status}`);
    this.status = status;
    this.body = body;
  }
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function setTokens(access: string, refresh: string): void {
  accessToken = access;
  localStorage.setItem(REFRESH_STORAGE_KEY, refresh);
}

export function clearTokens(): void {
  accessToken = null;
  localStorage.removeItem(REFRESH_STORAGE_KEY);
}

export function hasRefreshToken(): boolean {
  return Boolean(localStorage.getItem(REFRESH_STORAGE_KEY));
}

async function refreshAccessToken(): Promise<string | null> {
  if (refreshInFlight) {
    return refreshInFlight;
  }

  refreshInFlight = (async () => {
    const refresh = localStorage.getItem(REFRESH_STORAGE_KEY);
    if (!refresh) {
      return null;
    }
    const response = await fetch("/api/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!response.ok) {
      clearTokens();
      return null;
    }
    const data = (await response.json()) as { access: string };
    accessToken = data.access;
    return accessToken;
  })();

  try {
    return await refreshInFlight;
  } finally {
    refreshInFlight = null;
  }
}

export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers);
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response = await fetch(path, { ...options, headers });
  if (response.status === 401 && localStorage.getItem(REFRESH_STORAGE_KEY)) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      headers.set("Authorization", `Bearer ${newAccess}`);
      response = await fetch(path, { ...options, headers });
    }
  }
  return response;
}

export async function apiJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await apiFetch(path, options);
  if (!response.ok) {
    let body: ApiErrorBody = {};
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = {};
    }
    throw new ApiError(response.status, body);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function logoutApi(): Promise<void> {
  const refresh = localStorage.getItem(REFRESH_STORAGE_KEY);
  if (!refresh) {
    clearTokens();
    return;
  }
  try {
    await apiJson("/api/token/logout/", {
      method: "POST",
      body: JSON.stringify({ refresh }),
    });
  } catch {
    // Выход на клиенте выполняем даже при ошибке API.
  } finally {
    clearTokens();
  }
}
