/** Ранний запрос ленты с главной — стартует из inline-скрипта в index.html. */

import type { Paginated, Post } from "../api/types";

export const DEFAULT_FEED_PATH = "/api/posts/";

declare global {
  interface Window {
    __CREAVITY_FEED_PREFETCH__?: Promise<Paginated<Post>>;
  }
}

export function takeEarlyFeedPrefetch(path: string): Promise<Paginated<Post>> | null {
  if (path !== DEFAULT_FEED_PATH || !window.__CREAVITY_FEED_PREFETCH__) {
    return null;
  }
  const promise = window.__CREAVITY_FEED_PREFETCH__;
  delete window.__CREAVITY_FEED_PREFETCH__;
  return promise;
}
