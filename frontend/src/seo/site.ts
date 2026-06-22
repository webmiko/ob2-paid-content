/** Константы и утилиты SEO для SPA. */

export const SITE_NAME = "Creavity";
export const SITE_TAGLINE = "Платформа авторов и платного контента";
export const DEFAULT_DESCRIPTION =
  "Creavity — публикации авторов: бесплатные материалы для всех, платный контент по одной подписке на платформу.";

/** Версия в query — сброс агрессивного кэша favicon в браузере и PWA. */
export const FAVICON_HREF = "/favicon.svg?v=3";

const DEFAULT_SITE_URL = "http://localhost";

/** Базовый URL сайта из VITE_SITE_URL (без завершающего слэша). */
export function getSiteUrl(): string {
  const raw = import.meta.env.VITE_SITE_URL?.trim() || DEFAULT_SITE_URL;
  return raw.replace(/\/+$/, "");
}

/** Абсолютный URL для canonical и Open Graph. */
export function absoluteUrl(path = "/"): string {
  const base = getSiteUrl();
  if (!path || path === "/") {
    return `${base}/`;
  }
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

/** Обрезает текст до длины meta description. */
export function truncateDescription(text: string, maxLength = 160): string {
  const cleaned = text.replace(/\s+/g, " ").trim();
  if (cleaned.length <= maxLength) {
    return cleaned;
  }
  return `${cleaned.slice(0, maxLength - 1).trim()}…`;
}

/** Заголовок вкладки: «Страница | Creavity». */
export function buildPageTitle(pageTitle: string): string {
  if (pageTitle === SITE_NAME) {
    return SITE_NAME;
  }
  return `${pageTitle} | ${SITE_NAME}`;
}
