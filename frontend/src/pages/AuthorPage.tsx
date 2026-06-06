import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiJson } from "../api/client";
import type { AuthorSummary } from "../api/types";
import ContentTypeTabs from "../components/ContentTypeTabs";
import PostListSection from "../components/PostListSection";
import { usePostsList } from "../hooks/usePostsList";

export default function AuthorPage() {
  const { id } = useParams();
  const authorId = id ? Number(id) : NaN;
  const [author, setAuthor] = useState<AuthorSummary | null>(null);
  const [content, setContent] = useState<"all" | "free" | "paid" | "available">("all");
  const [pageError, setPageError] = useState<string | null>(null);

  const filters = useMemo(
    () => ({
      content,
      author: Number.isFinite(authorId) ? authorId : undefined,
    }),
    [content, authorId],
  );
  const { posts, error, loading, loadingMore, nextPath, loadMore } = usePostsList(filters);

  useEffect(() => {
    if (!Number.isFinite(authorId)) {
      return;
    }
    const load = async () => {
      try {
        const data = await apiJson<AuthorSummary>(`/api/posts/authors/${authorId}/`);
        setAuthor(data);
      } catch {
        setPageError("Автор не найден.");
      }
    };
    void load();
  }, [authorId]);

  if (pageError) {
    return (
      <div className="alert-custom alert-danger-custom">
        {pageError}{" "}
        <Link className="text-link" to="/explore">
          К каталогу
        </Link>
      </div>
    );
  }

  return (
    <section>
      <Link className="back-link" to="/explore">
        ← К каталогу
      </Link>
      <div className="card author-header">
        <div className="author-header-icon">
          <i className="fa-solid fa-user-pen" aria-hidden="true" />
        </div>
        <div>
          <h1 className="page-title">{author?.label ?? "Автор"}</h1>
          {author && (
            <p className="page-subtitle mb-0">
              {author.post_count} публикаций · {author.free_count} бесплатных · {author.paid_count} платных
            </p>
          )}
        </div>
      </div>

      <ContentTypeTabs value={content} onChange={setContent} />

      <PostListSection
        posts={posts}
        error={error}
        loading={loading || !author}
        loadingMore={loadingMore}
        nextPath={nextPath}
        onLoadMore={() => void loadMore()}
        emptyTitle="У автора пока нет публикаций в этой категории"
      />
    </section>
  );
}
