import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiJson } from "../api/client";
import type { Post } from "../api/types";
import PaywallBanner from "../components/PaywallBanner";
import JsonLd from "../components/JsonLd";
import PageMeta from "../components/PageMeta";
import PostBadge from "../components/PostBadge";
import PostCard from "../components/PostCard";
import PostComments from "../components/PostComments";
import PostVideo from "../components/PostVideo";
import { formatPostDate } from "../utils/avatar";
import { markPostViewed } from "../utils/viewedPosts";
import { absoluteUrl, getSiteUrl, truncateDescription, SITE_NAME } from "../seo/site";

export default function PostDetailPage() {
  const { id } = useParams();
  const [post, setPost] = useState<Post | null>(null);
  const [similar, setSimilar] = useState<Post[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) {
      return;
    }
    const load = async () => {
      try {
        const data = await apiJson<Post>(`/api/posts/${id}/`);
        setPost(data);
        markPostViewed(data.id);
        void apiJson(`/api/posts/${id}/view/`, { method: "POST" }).catch(() => undefined);
        const similarData = await apiJson<Post[]>(`/api/posts/${id}/similar/`);
        setSimilar(similarData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось загрузить публикацию.");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [id]);

  const postPath = id ? `/posts/${id}` : "/";

  if (loading) {
    return (
      <>
        <PageMeta title="Публикация" path={postPath} />
        <p className="loading-text">Загрузка…</p>
      </>
    );
  }

  if (error || !post) {
    return (
      <>
        <PageMeta
          title="Публикация не найдена"
          description="Запрошенная публикация не существует или была удалена."
          path={postPath}
          noIndex
        />
        <div className="alert-custom alert-danger-custom">
          {error ?? "Публикация не найдена"}{" "}
          <Link className="text-link" to="/">
            В ленту
          </Link>
        </div>
      </>
    );
  }

  const postDescription = post.can_view_body && post.body
    ? truncateDescription(post.body)
    : post.is_paid
      ? `Платная публикация «${post.title}» автора ${post.author_label} на Creavity.`
      : truncateDescription(`${post.title}. ${post.author_label} на Creavity.`);

  return (
    <>
      <PageMeta
        title={post.title}
        description={postDescription}
        path={`/posts/${post.id}`}
        ogType="article"
        publishedTime={post.created_at}
        modifiedTime={post.updated_at}
        authorName={post.author_label}
      />
      <JsonLd
        data={[
          {
            "@context": "https://schema.org",
            "@type": "Article",
            headline: post.title,
            description: postDescription,
            url: absoluteUrl(`/posts/${post.id}`),
            datePublished: post.created_at,
            dateModified: post.updated_at,
            author: {
              "@type": "Person",
              name: post.author_label,
              url: absoluteUrl(`/authors/${post.author_id}`),
            },
            publisher: {
              "@type": "Organization",
              name: SITE_NAME,
              url: getSiteUrl(),
            },
            mainEntityOfPage: absoluteUrl(`/posts/${post.id}`),
            isAccessibleForFree: !post.is_paid,
            inLanguage: "ru-RU",
          },
          {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              {
                "@type": "ListItem",
                position: 1,
                name: "Лента",
                item: absoluteUrl("/"),
              },
              {
                "@type": "ListItem",
                position: 2,
                name: post.topic_label,
                item: absoluteUrl(`/topics/${post.topic}`),
              },
              {
                "@type": "ListItem",
                position: 3,
                name: post.title,
                item: absoluteUrl(`/posts/${post.id}`),
              },
            ],
          },
        ]}
      />
      <article>
      <Link className="back-link" to="/">
        ← В ленту
      </Link>
      <div className="card">
        <div className="post-header">
          <div className="post-meta">
            <Link to={`/authors/${post.author_id}`} className="author-label author-link">
              {post.author_label}
            </Link>
            <PostBadge isPaid={post.is_paid} />
            <Link to={`/topics/${post.topic}`} className="topic-chip topic-link">
              {post.topic_label}
            </Link>
          </div>
          <span className="post-date">{formatPostDate(post.created_at)}</span>
        </div>
        <h1 className="post-title">{post.title}</h1>
        <PostVideo post={post} />
        {post.can_view_body && post.body ? (
          <p className="post-content" style={{ whiteSpace: "pre-wrap" }}>
            {post.body}
          </p>
        ) : (
          <PaywallBanner />
        )}
      </div>
      <PostComments
        postId={post.id}
        canAccess={post.can_view_body}
        initialCount={post.comment_count}
      />
      {similar.length > 0 && (
        <section className="similar-section">
          <h2 className="section-title">
            <i className="fa-solid fa-layer-group" aria-hidden="true" /> Похожие материалы
          </h2>
          {similar.map((item) => (
            <PostCard key={item.id} post={item} />
          ))}
        </section>
      )}
    </article>
    </>
  );
}
