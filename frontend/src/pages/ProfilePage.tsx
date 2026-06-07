import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import { apiJson } from "../api/client";
import type {
  AuthorDashboardStats,
  Paginated,
  PaymentCreateResponse,
  PaymentSuccessResponse,
  Post,
} from "../api/types";
import AuthorDashboard from "../components/AuthorDashboard";
import DeleteAccountSection from "../components/DeleteAccountSection";
import PageMeta from "../components/PageMeta";
import PostBadge from "../components/PostBadge";
import PostEditForm from "../components/PostEditForm";
import { TOPICS } from "../constants/topics";
import { useAuth } from "../context/AuthContext";
import { formatPostDate, userNickname } from "../utils/avatar";
import { topicCardClassName } from "../utils/topicStyles";
import { VIDEO_URL_PLACEHOLDER } from "../utils/videoProviders";

export default function ProfilePage() {
  const { user, loading, isAuthenticated, refreshProfile } = useAuth();
  const [payError, setPayError] = useState<string | null>(null);
  const [payLoading, setPayLoading] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [nameMessage, setNameMessage] = useState<string | null>(null);
  const [postTitle, setPostTitle] = useState("");
  const [postBody, setPostBody] = useState("");
  const [postPaid, setPostPaid] = useState(false);
  const [postTopic, setPostTopic] = useState("other");
  const [postVideoUrl, setPostVideoUrl] = useState("");
  const [postMessage, setPostMessage] = useState<string | null>(null);
  const [myPosts, setMyPosts] = useState<Post[]>([]);
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [dashboardStats, setDashboardStats] = useState<AuthorDashboardStats | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);

  const myPostsPath = useMemo(
    () => (user ? `/api/posts/?author=${user.id}` : null),
    [user],
  );

  useEffect(() => {
    if (user) {
      setDisplayName(user.display_name);
    }
  }, [user]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    const loadStats = async () => {
      try {
        const data = await apiJson<AuthorDashboardStats>("/api/users/me/stats/");
        setDashboardStats(data);
        setDashboardError(null);
      } catch {
        setDashboardStats(null);
        setDashboardError("Не удалось загрузить статистику.");
      }
    };
    void loadStats();
  }, [isAuthenticated, postMessage]);

  useEffect(() => {
    if (!myPostsPath) {
      return;
    }
    const load = async () => {
      try {
        const data = await apiJson<Paginated<Post>>(myPostsPath);
        setMyPosts(data.results);
      } catch {
        setMyPosts([]);
      }
    };
    void load();
  }, [myPostsPath, postMessage]);

  const reloadMyPosts = async () => {
    if (!myPostsPath) {
      return;
    }
    try {
      const data = await apiJson<Paginated<Post>>(myPostsPath);
      setMyPosts(data.results);
    } catch {
      setMyPosts([]);
    }
  };

  if (loading) {
    return <p className="loading-text">Загрузка профиля…</p>;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  const handlePay = async () => {
    setPayLoading(true);
    setPayError(null);
    try {
      const data = await apiJson<PaymentCreateResponse>("/api/payments/create/", {
        method: "POST",
      });
      window.location.href = data.payment_url;
    } catch {
      setPayError("Не удалось создать платёж. Попробуйте позже.");
      setPayLoading(false);
    }
  };

  const handleSyncSubscription = async () => {
    setPayError(null);
    try {
      await apiJson<PaymentSuccessResponse>("/api/payments/sync/", { method: "POST" });
      await refreshProfile();
    } catch {
      setPayError("Не удалось проверить оплату. Попробуйте позже.");
    }
  };

  const handleSaveName = async (event: FormEvent) => {
    event.preventDefault();
    setNameMessage(null);
    try {
      await apiJson("/api/users/me/", {
        method: "PATCH",
        body: JSON.stringify({ display_name: displayName }),
      });
      await refreshProfile();
      setNameMessage("Никнейм сохранён.");
    } catch {
      setNameMessage("Не удалось сохранить никнейм.");
    }
  };

  const handleCreatePost = async (event: FormEvent) => {
    event.preventDefault();
    setPostMessage(null);
    try {
      await apiJson("/api/posts/", {
        method: "POST",
        body: JSON.stringify({
          title: postTitle,
          body: postBody,
          is_paid: postPaid,
          topic: postTopic,
          video_url: postVideoUrl.trim(),
        }),
      });
      setPostTitle("");
      setPostBody("");
      setPostPaid(false);
      setPostTopic("other");
      setPostVideoUrl("");
      setPostMessage("Публикация создана.");
    } catch {
      setPostMessage("Не удалось создать публикацию.");
    }
  };

  return (
    <>
      <PageMeta
        title="Мой профиль"
        description="Личный кабинет автора Creavity."
        path="/profile"
        noIndex
      />
      <section>
      <h1 className="page-title">
        <i className="fa-solid fa-user-circle" aria-hidden="true" /> Мой профиль
      </h1>

      <div className="profile-grid">
        <div className="card">
          <h2 className="section-title">
            <i className="fa-solid fa-id-card" aria-hidden="true" /> Аккаунт
          </h2>
          <p>
            <strong>Никнейм:</strong> {userNickname(user.display_name)}
          </p>
          <p className="hint-text">
            Телефон {user.phone} используется только для входа и не показывается в ленте.
          </p>
          <p className="mb-0">
            <strong>Подписка:</strong>{" "}
            <span className={`badge-type ${user.subscription_active ? "badge-active" : "badge-inactive"}`}>
              {user.subscription_active ? "Активна" : "Не активна"}
            </span>
          </p>
          {!user.subscription_active && (
            <div className="mt-3">
              {payError && <div className="alert-custom alert-danger-custom">{payError}</div>}
              <button type="button" className="btn-pill" onClick={handlePay} disabled={payLoading}>
                {payLoading ? "Переход к оплате…" : "Оплатить подписку платформы"}
              </button>
              <p className="hint-text">
                Одна подписка открывает платный контент всех авторов на Creavity.
              </p>
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="section-title">
            <i className="fa-solid fa-signature" aria-hidden="true" /> Никнейм
          </h2>
          {nameMessage && <div className="alert-custom alert-info-custom">{nameMessage}</div>}
          <form onSubmit={handleSaveName}>
            <div className="form-group">
              <label htmlFor="display_name">Как вас видят на платформе</label>
              <input
                id="display_name"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                placeholder="Ваш никнейм"
                minLength={2}
                maxLength={80}
                required
              />
            </div>
            <button type="submit" className="btn-pill btn-pill-secondary">
              Сохранить
            </button>
          </form>
        </div>
      </div>

      {dashboardError && <div className="alert-custom alert-warning-custom">{dashboardError}</div>}
      {dashboardStats && <AuthorDashboard stats={dashboardStats} />}

      <h2 className="section-title">
        <i className="fa-solid fa-feather" aria-hidden="true" /> Новая публикация
      </h2>
      <div className="card">
        {postMessage && <div className="alert-custom alert-info-custom">{postMessage}</div>}
        <form onSubmit={handleCreatePost}>
          <div className="form-group">
            <label htmlFor="title">Заголовок</label>
            <input
              id="title"
              value={postTitle}
              onChange={(e) => setPostTitle(e.target.value)}
              placeholder="Яркий заголовок"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="topic">Тематика</label>
            <select id="topic" value={postTopic} onChange={(e) => setPostTopic(e.target.value)}>
              {TOPICS.map((item) => (
                <option key={item.slug} value={item.slug}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="body">Текст</label>
            <textarea
              id="body"
              rows={4}
              value={postBody}
              onChange={(e) => setPostBody(e.target.value)}
              placeholder="Ваш текст…"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="video_url">Видео (необязательно)</label>
            <input
              id="video_url"
              type="url"
              value={postVideoUrl}
              onChange={(e) => setPostVideoUrl(e.target.value)}
              placeholder={VIDEO_URL_PLACEHOLDER}
            />
          </div>
          <div className="form-check-custom">
            <input
              id="is_paid"
              type="checkbox"
              checked={postPaid}
              onChange={(e) => setPostPaid(e.target.checked)}
            />
            <label htmlFor="is_paid">Платная публикация (доступ по подписке платформы)</label>
          </div>
          <button type="submit" className="btn-pill">
            Опубликовать
          </button>
        </form>
      </div>

      <h2 className="section-title">
        <i className="fa-solid fa-folder-open" aria-hidden="true" /> Мои публикации
      </h2>
      {myPosts.length === 0 ? (
        <div className="empty-state">
          <p>Вы ещё не публиковали материалы</p>
        </div>
      ) : (
        myPosts.map((post) => (
          <div
            key={post.id}
            className={`${topicCardClassName(post.topic)} compact-post-card profile-post-item`}
          >
            {editingPostId === post.id ? (
              <PostEditForm
                post={post}
                onSaved={() => {
                  setEditingPostId(null);
                  setPostMessage("Публикация обновлена.");
                  void reloadMyPosts();
                }}
                onCancel={() => setEditingPostId(null)}
              />
            ) : (
              <>
                <div className="post-header">
                  <div className="post-meta">
                    <PostBadge isPaid={post.is_paid} />
                    <span className="topic-chip">{post.topic_label}</span>
                    {post.has_video && (
                      <span className="video-chip">
                        <i className="fa-solid fa-video" aria-hidden="true" /> Видео
                      </span>
                    )}
                  </div>
                  <span className="post-date">{formatPostDate(post.created_at)}</span>
                </div>
                <h3 className="post-title">{post.title}</h3>
                <div className="post-edit-actions">
                  <Link to={`/posts/${post.id}`} className="text-link">
                    Открыть
                  </Link>
                  <button
                    type="button"
                    className="btn-pill btn-pill-outline btn-sm-pill"
                    onClick={() => setEditingPostId(post.id)}
                  >
                    Редактировать
                  </button>
                </div>
              </>
            )}
          </div>
        ))
      )}

      <div className="profile-actions">
        <button type="button" className="btn-pill btn-pill-secondary btn-sm-pill" onClick={() => void refreshProfile()}>
          Обновить профиль
        </button>
        {!user.subscription_active && (
          <button
            type="button"
            className="btn-pill btn-pill-outline btn-sm-pill"
            onClick={() => void handleSyncSubscription()}
          >
            Проверить оплату
          </button>
        )}
      </div>

      <DeleteAccountSection phone={user.phone} />
    </section>
    </>
  );
}
