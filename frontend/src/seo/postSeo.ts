import type { Post } from "../api/types";
import { absoluteUrl, getSiteUrl, SITE_NAME } from "./site";
import type { PageMetaOptions } from "./usePageMeta";

/** Meta-теги страницы публикации из API (автогенерация на бэкенде). */
export function postPageMetaOptions(post: Post): PageMetaOptions {
  return {
    title: post.meta_title || post.title,
    description: post.meta_description || post.title,
    keywords: post.meta_keywords || undefined,
    path: `/posts/${post.id}`,
    ogType: "article",
    publishedTime: post.created_at,
    modifiedTime: post.updated_at,
    authorName: post.author_label,
  };
}

/** JSON-LD Article и хлебные крошки для страницы публикации. */
export function postJsonLdData(post: Post): Record<string, unknown>[] {
  const description = post.meta_description || post.title;
  const pageUrl = absoluteUrl(`/posts/${post.id}`);

  return [
    {
      "@context": "https://schema.org",
      "@type": "Article",
      headline: post.meta_title || post.title,
      description,
      keywords: post.meta_keywords || undefined,
      url: pageUrl,
      datePublished: post.created_at,
      dateModified: post.updated_at,
      author: {
        "@type": "Person",
        name: post.author_label,
        url: absoluteUrl(`/authors/${post.author_id}`),
      },
      publisher: {
        "@type": "Organization",
        name: SITE_NAME,
        url: getSiteUrl(),
      },
      mainEntityOfPage: pageUrl,
      isAccessibleForFree: !post.is_paid,
      inLanguage: "ru-RU",
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: [
        {
          "@type": "ListItem",
          position: 1,
          name: "Лента",
          item: absoluteUrl("/"),
        },
        {
          "@type": "ListItem",
          position: 2,
          name: post.topic_label,
          item: absoluteUrl(`/topics/${post.topic}`),
        },
        {
          "@type": "ListItem",
          position: 3,
          name: post.title,
          item: pageUrl,
        },
      ],
    },
  ];
}
