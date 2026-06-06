import { useCallback, useEffect, useState } from "react";

import { apiJson } from "../api/client";
import type { Paginated, Post } from "../api/types";

export type ContentFilter = "all" | "free" | "paid" | "available";

export interface PostListFilters {
  content: ContentFilter;
  topic?: string;
  author?: number;
  search?: string;
}

function apiPathFromPaginatedUrl(next: string | null): string | null {
  if (!next) {
    return null;
  }
  try {
    const url = new URL(next, window.location.origin);
    return `${url.pathname}${url.search}`;
  } catch {
    return next;
  }
}

function buildPostsPath(filters: PostListFilters): string {
  const params = new URLSearchParams();
  if (filters.content === "free") {
    params.set("is_paid", "false");
  } else if (filters.content === "paid") {
    params.set("is_paid", "true");
  } else if (filters.content === "available") {
    params.set("access", "available");
  }
  if (filters.topic) {
    params.set("topic", filters.topic);
  }
  if (filters.author) {
    params.set("author", String(filters.author));
  }
  if (filters.search?.trim()) {
    params.set("search", filters.search.trim());
  }
  const query = params.toString();
  return query ? `/api/posts/?${query}` : "/api/posts/";
}

export function usePostsList(filters: PostListFilters) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [nextPath, setNextPath] = useState<string | null>(null);

  const loadPage = useCallback(async (path: string, append: boolean) => {
    const data = await apiJson<Paginated<Post>>(path);
    setPosts((prev) => (append ? [...prev, ...data.results] : data.results));
    setNextPath(apiPathFromPaginatedUrl(data.next));
  }, []);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        await loadPage(buildPostsPath(filters), false);
      } catch {
        setError("Не удалось загрузить публикации.");
        setPosts([]);
        setNextPath(null);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [filters.content, filters.topic, filters.author, filters.search, loadPage]);

  const loadMore = async () => {
    if (!nextPath) {
      return;
    }
    setLoadingMore(true);
    setError(null);
    try {
      await loadPage(nextPath, true);
    } catch {
      setError("Не удалось загрузить следующую страницу.");
    } finally {
      setLoadingMore(false);
    }
  };

  return { posts, error, loading, loadingMore, nextPath, loadMore };
}
