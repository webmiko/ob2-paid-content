const VIEWED_STORAGE_KEY = "creavity_viewed_posts";
const MAX_VIEWED = 200;

export function getViewedPostIds(): number[] {
  try {
    const raw = localStorage.getItem(VIEWED_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter((item): item is number => typeof item === "number");
  } catch {
    return [];
  }
}

export function markPostViewed(postId: number): void {
  const current = getViewedPostIds().filter((id) => id !== postId);
  current.unshift(postId);
  localStorage.setItem(VIEWED_STORAGE_KEY, JSON.stringify(current.slice(0, MAX_VIEWED)));
}

export function buildExcludeQuery(ids: number[]): string {
  if (ids.length === 0) {
    return "";
  }
  return `?exclude=${ids.join(",")}`;
}
