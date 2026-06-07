interface PostListSkeletonProps {
  count?: number;
}

export default function PostListSkeleton({ count = 3 }: PostListSkeletonProps) {
  return (
    <div className="post-list-skeleton" aria-busy="true" aria-label="Загрузка публикаций">
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="card post-card-skeleton">
          <div className="post-card-skeleton-meta" />
          <div className="post-card-skeleton-title" />
          <div className="post-card-skeleton-line" />
          <div className="post-card-skeleton-line post-card-skeleton-line--short" />
        </div>
      ))}
    </div>
  );
}
