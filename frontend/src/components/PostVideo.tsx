import type { Post } from "../api/types";
import { videoProviderLabel } from "../utils/videoProviders";

interface PostVideoProps {
  post: Post;
}

export default function PostVideo({ post }: PostVideoProps) {
  const providerLabel = videoProviderLabel(post.video_provider);

  if (post.video_embed_url) {
    return (
      <div className="post-video-block">
        {providerLabel && <p className="post-video-label">Видео · {providerLabel}</p>}
        <div className="post-video-wrap">
          <iframe
            title={`Видео: ${post.title}`}
            src={post.video_embed_url}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </div>
    );
  }

  if (post.has_video && !post.can_view_body) {
    return (
      <p className="post-preview-muted">
        <i className="fa-solid fa-video" aria-hidden="true" /> Видео
        {providerLabel ? ` (${providerLabel})` : ""} доступно по подписке платформы
      </p>
    );
  }

  return null;
}
