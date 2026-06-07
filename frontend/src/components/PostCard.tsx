import { Link } from "react-router-dom";

import type { Post } from "../api/types";
import { videoProviderLabel } from "../utils/videoProviders";
import PostBadge from "./PostBadge";
import ProtectedPaidPost from "./ProtectedPaidPost";
import { formatPostDate } from "../utils/avatar";
import { topicChipClassName } from "../utils/topicStyles";

interface PostCardProps {
  post: Post;
}

export default function PostCard({ post }: PostCardProps) {
  const providerLabel = videoProviderLabel(post.video_provider);

  return (
    <article className="card post-card">
      <div className="post-header">
        <div className="post-meta">
          <Link to={`/authors/${post.author_id}`} className="author-label author-link">
            {post.author_label}
          </Link>
          <PostBadge isPaid={post.is_paid} />
          {post.has_video && (
            <span className="video-chip" title={providerLabel ?? "Видео"}>
              <i className="fa-solid fa-video" aria-hidden="true" />
              {providerLabel ?? "Видео"}
              {post.is_paid && !post.can_view_body && (
                <i className="fa-solid fa-lock video-chip-lock" aria-hidden="true" />
              )}
            </span>
          )}
          <Link
            to={`/topics/${post.topic}`}
            className={topicChipClassName(post.topic, "topic-link")}
          >
            {post.topic_label}
          </Link>
        </div>
        <span className="post-date">{formatPostDate(post.created_at)}</span>
      </div>
      <Link to={`/posts/${post.id}`} className="post-card-body-link">
        <h2 className="post-title">{post.title}</h2>
        {post.can_view_body && post.body ? (
          <ProtectedPaidPost post={post}>
            <p className="post-content">{post.body}</p>
          </ProtectedPaidPost>
        ) : (
          <p className="post-preview-muted">
            <i className="fa-solid fa-lock" aria-hidden="true" /> Текст скрыт — нужна подписка платформы
          </p>
        )}
        {post.comment_count > 0 && (
          <p className="post-card-comments">
            <i className="fa-solid fa-comments" aria-hidden="true" /> {post.comment_count} коммент.
          </p>
        )}
      </Link>
    </article>
  );
}
