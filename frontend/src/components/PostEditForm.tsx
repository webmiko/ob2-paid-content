import type { FormEvent } from "react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { apiJson } from "../api/client";
import type { Post } from "../api/types";
import { TOPICS } from "../constants/topics";
import { VIDEO_URL_PLACEHOLDER } from "../utils/videoProviders";

interface PostEditFormProps {
  post: Post;
  onSaved: () => void;
  onCancel: () => void;
}

export default function PostEditForm({ post, onSaved, onCancel }: PostEditFormProps) {
  const [title, setTitle] = useState(post.title);
  const [body, setBody] = useState(post.body ?? "");
  const [topic, setTopic] = useState(post.topic);
  const [videoUrl, setVideoUrl] = useState(post.video_url ?? "");
  const [isPaid, setIsPaid] = useState(post.is_paid);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await apiJson(`/api/posts/${post.id}/`, {
        method: "PATCH",
        body: JSON.stringify({
          title,
          body,
          topic,
          is_paid: isPaid,
          video_url: videoUrl.trim(),
        }),
      });
      onSaved();
    } catch {
      setError("Не удалось сохранить изменения.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="post-edit-form" onSubmit={handleSubmit}>
      {error && <div className="alert-custom alert-warning-custom">{error}</div>}
      <div className="form-group">
        <label htmlFor={`title-${post.id}`}>Заголовок</label>
        <input
          id={`title-${post.id}`}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor={`topic-${post.id}`}>Тематика</label>
        <select id={`topic-${post.id}`} value={topic} onChange={(event) => setTopic(event.target.value)}>
          {TOPICS.map((item) => (
            <option key={item.slug} value={item.slug}>
              {item.label}
            </option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label htmlFor={`body-${post.id}`}>Текст</label>
        <textarea
          id={`body-${post.id}`}
          rows={4}
          value={body}
          onChange={(event) => setBody(event.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor={`video-${post.id}`}>Видео (необязательно)</label>
        <input
          id={`video-${post.id}`}
          type="url"
          value={videoUrl}
          onChange={(event) => setVideoUrl(event.target.value)}
          placeholder={VIDEO_URL_PLACEHOLDER}
        />
      </div>
      <div className="form-check-custom">
        <input
          id={`paid-${post.id}`}
          type="checkbox"
          checked={isPaid}
          onChange={(event) => setIsPaid(event.target.checked)}
        />
        <label htmlFor={`paid-${post.id}`}>Платная публикация</label>
      </div>
      <div className="post-edit-actions">
        <button type="submit" className="btn-pill btn-sm-pill" disabled={saving}>
          {saving ? "Сохранение…" : "Сохранить"}
        </button>
        <button type="button" className="btn-pill btn-pill-outline btn-sm-pill" onClick={onCancel}>
          Отмена
        </button>
        <Link to={`/posts/${post.id}`} className="text-link">
          Открыть
        </Link>
      </div>
    </form>
  );
}
