import { useEffect } from "react";

import {
  absoluteUrl,
  buildPageTitle,
  DEFAULT_DESCRIPTION,
  FAVICON_HREF,
  getSiteUrl,
  SITE_NAME,
} from "../seo/site";

export interface PageMetaOptions {
  title: string;
  description?: string;
  path?: string;
  noIndex?: boolean;
  ogType?: "website" | "article";
  publishedTime?: string;
  modifiedTime?: string;
  authorName?: string;
  keywords?: string;
}

function upsertMeta(attribute: "name" | "property", key: string, content: string): void {
  const selector = `meta[${attribute}="${key}"]`;
  let element = document.head.querySelector(selector);
  if (!element) {
    element = document.createElement("meta");
    element.setAttribute(attribute, key);
    document.head.appendChild(element);
  }
  element.setAttribute("content", content);
}

function upsertLink(rel: string, href: string, extra?: Record<string, string>): void {
  let element = document.head.querySelector(`link[rel="${rel}"]`);
  if (!element) {
    element = document.createElement("link");
    element.setAttribute("rel", rel);
    document.head.appendChild(element);
  }
  element.setAttribute("href", href);
  if (extra) {
    for (const [name, value] of Object.entries(extra)) {
      element.setAttribute(name, value);
    }
  }
}

function applyPageMeta(options: PageMetaOptions): void {
  const {
    title,
    description = DEFAULT_DESCRIPTION,
    path = "/",
    noIndex = false,
    ogType = "website",
    publishedTime,
    modifiedTime,
    authorName,
    keywords,
  } = options;

  const pageTitle = buildPageTitle(title);
  const canonical = absoluteUrl(path);
  const ogImage = absoluteUrl("/og-default.svg");
  const robots = noIndex ? "noindex, nofollow" : "index, follow, max-image-preview:large";

  document.title = pageTitle;
  upsertMeta("name", "description", description);
  upsertMeta("name", "robots", robots);
  if (keywords?.trim()) {
    upsertMeta("name", "keywords", keywords.trim());
  } else {
    document.head.querySelector('meta[name="keywords"]')?.remove();
  }
  upsertLink("canonical", canonical);
  upsertLink("icon", FAVICON_HREF, { type: "image/svg+xml" });
  upsertLink("alternate", getSiteUrl(), { hreflang: "ru" });

  upsertMeta("property", "og:site_name", SITE_NAME);
  upsertMeta("property", "og:locale", "ru_RU");
  upsertMeta("property", "og:type", ogType);
  upsertMeta("property", "og:title", pageTitle);
  upsertMeta("property", "og:description", description);
  upsertMeta("property", "og:url", canonical);
  upsertMeta("property", "og:image", ogImage);
  upsertMeta("property", "og:image:alt", `${SITE_NAME} — платформа авторов`);

  upsertMeta("name", "twitter:card", "summary_large_image");
  upsertMeta("name", "twitter:title", pageTitle);
  upsertMeta("name", "twitter:description", description);
  upsertMeta("name", "twitter:image", ogImage);

  if (ogType === "article" && publishedTime) {
    upsertMeta("property", "article:published_time", publishedTime);
  }
  if (ogType === "article" && modifiedTime) {
    upsertMeta("property", "article:modified_time", modifiedTime);
  }
  if (ogType === "article" && authorName) {
    upsertMeta("property", "article:author", authorName);
  }
}

/** Обновляет meta-теги и title при смене маршрута. */
export function usePageMeta(options: PageMetaOptions): void {
  useEffect(() => {
    applyPageMeta(options);
    return () => {
      applyPageMeta({ title: SITE_NAME, path: "/" });
    };
  }, [
    options.title,
    options.description,
    options.path,
    options.noIndex,
    options.ogType,
    options.publishedTime,
    options.modifiedTime,
    options.authorName,
    options.keywords,
  ]);
}
