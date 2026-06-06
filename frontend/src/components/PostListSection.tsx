import PostCard from "./PostCard";
import type { Post } from "../api/types";

interface PostListSectionProps {
  posts: Post[];
  error: string | null;
  loading: boolean;
  loadingMore: boolean;
  nextPath: string | null;
  onLoadMore: () => void;
  emptyTitle?: string;
  emptyText?: string;
}

export default function PostListSection({
  posts,
  error,
  loading,
  loadingMore,
  nextPath,
  onLoadMore,
  emptyTitle = "Пока нет публикаций",
  emptyText = "Попробуйте другие фильтры или загляните позже",
}: PostListSectionProps) {
  if (loading) {
    return <p className="loading-text">Загрузка публикаций…</p>;
  }

  if (error && posts.length === 0) {
    return <div className="alert-custom alert-danger-custom">{error}</div>;
  }

  return (
    <>
      {error && <div className="alert-custom alert-warning-custom">{error}</div>}
      {posts.length === 0 ? (
        <div className="empty-state">
          <i className="fa-solid fa-newspaper fa-2x" aria-hidden="true" />
          <h3>{emptyTitle}</h3>
          <p>{emptyText}</p>
        </div>
      ) : (
        posts.map((post) => <PostCard key={post.id} post={post} />)
      )}
      {nextPath && (
        <button
          type="button"
          className="btn-pill btn-pill-outline"
          onClick={onLoadMore}
          disabled={loadingMore}
        >
          {loadingMore ? "Загрузка…" : "Показать ещё"}
        </button>
      )}
    </>
  );
}
