import type { Post } from "../api/types";

/** Нужна ли клиентская защита от копирования (не для автора своего поста). */
export function shouldProtectPaidContent(post: Post, userId?: number | null): boolean {
  return post.is_paid && post.can_view_body && userId !== post.author_id;
}
