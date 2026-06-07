import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiJson } from "../api/client";
import type { AuthorSummary, Post, TopicSummary } from "../api/types";
import PostCard from "../components/PostCard";
import JsonLd from "../components/JsonLd";
import PageMeta from "../components/PageMeta";
import { useAuth } from "../context/AuthContext";
import { buildExcludeQuery, getViewedPostIds } from "../utils/viewedPosts";
import { absoluteUrl } from "../seo/site";

export default function ExplorePage() {
  const { isAuthenticated } = useAuth();
  const [authors, setAuthors] = useState<AuthorSummary[]>([]);
  const [topics, setTopics] = useState<TopicSummary[]>([]);
  const [recommended, setRecommended] = useState<Post[]>([]);
  const [authorSearch, setAuthorSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const excludeQuery = buildExcludeQuery(getViewedPostIds());
        const [authorsData, topicsData, recommendedData] = await Promise.all([
          apiJson<AuthorSummary[]>("/api/posts/authors/"),
          apiJson<TopicSummary[]>("/api/posts/topics/"),
          apiJson<Post[]>(`/api/posts/recommended${excludeQuery}`),
        ]);
        setAuthors(authorsData);
        setTopics(topicsData.filter((item) => item.post_count > 0));
        setRecommended(recommendedData);
      } catch {
        setError("Не удалось загрузить каталог.");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  useEffect(() => {
    const timeout = setTimeout(async () => {
      try {
        const query = authorSearch.trim()
          ? `?search=${encodeURIComponent(authorSearch.trim())}`
          : "";
        const data = await apiJson<AuthorSummary[]>(`/api/posts/authors/${query}`);
        setAuthors(data);
      } catch {
        setError("Не удалось найти авторов.");
      }
    }, 300);
    return () => clearTimeout(timeout);
  }, [authorSearch]);

  if (loading) {
    return (
      <>
        <PageMeta
          title="Каталог авторов и тем"
          description="Авторы, тематики и рекомендуемые публикации Creavity."
          path="/explore"
        />
        <p className="loading-text">Загрузка каталога…</p>
      </>
    );
  }

  return (
    <>
      <PageMeta
        title="Каталог авторов и тем"
        description="Авторы, тематики и рекомендуемые публикации Creavity. Одна подписка открывает весь платный контент платформы."
        path="/explore"
      />
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "CollectionPage",
          name: "Каталог авторов и тем",
          url: absoluteUrl("/explore"),
          description: "Авторы, тематики и рекомендуемые публикации Creavity.",
          inLanguage: "ru-RU",
        }}
      />
      <section>
      <h1 className="page-title">
        <i className="fa-solid fa-table-cells-large" aria-hidden="true" /> Каталог авторов и тем
      </h1>
      <p className="page-subtitle">
        Выберите автора или тематику. Подписка одна на всю платформу — не на отдельных авторов.
      </p>
      {error && <div className="alert-custom alert-warning-custom">{error}</div>}

      <h2 className="section-title">
        <i className="fa-solid fa-wand-magic-sparkles" aria-hidden="true" /> Рекомендуем
      </h2>
      <p className="hint-text explore-hint">
        Бесплатные материалы разных тем — попробуйте перед оформлением подписки на платный контент.
      </p>
      {recommended.length === 0 ? (
        <p className="text-muted">Пока нет рекомендаций</p>
      ) : (
        recommended.map((post) => <PostCard key={post.id} post={post} />)
      )}

      <h2 className="section-title">
        <i className="fa-solid fa-users" aria-hidden="true" /> Авторы
      </h2>
      <div className="filter-search explore-search">
        <i className="fa-solid fa-magnifying-glass" aria-hidden="true" />
        <input
          type="search"
          value={authorSearch}
          onChange={(event) => setAuthorSearch(event.target.value)}
          placeholder="Поиск автора по имени…"
          aria-label="Поиск авторов"
        />
      </div>
      <div className="explore-grid">
        {authors.length === 0 ? (
          <p className="text-muted">Авторы не найдены</p>
        ) : (
          authors.map((author) => (
            <Link key={author.id} to={`/authors/${author.id}`} className="card explore-card">
              <div className="explore-card-icon">
                <i className="fa-solid fa-user-pen" aria-hidden="true" />
              </div>
              <h3>{author.label}</h3>
              <p className="explore-card-meta">
                {author.post_count} публ. · {author.free_count} беспл. · {author.paid_count} платн.
              </p>
            </Link>
          ))
        )}
      </div>

      <h2 className="section-title">
        <i className="fa-solid fa-tags" aria-hidden="true" /> Тематики
      </h2>
      <div className="explore-grid">
        {topics.map((topic) => (
          <Link key={topic.slug} to={`/topics/${topic.slug}`} className="card explore-card">
            <div className="explore-card-icon topic-icon">
              <i className="fa-solid fa-hashtag" aria-hidden="true" />
            </div>
            <h3>{topic.label}</h3>
            <p className="explore-card-meta">{topic.post_count} публикаций</p>
          </Link>
        ))}
      </div>

      {!isAuthenticated && (
        <div className="card catalog-cta">
          <p className="mb-0">
            Понравился материал?{" "}
            <Link className="text-link" to="/register">
              Зарегистрируйтесь
            </Link>{" "}
            и оформите подписку платформы для доступа ко всем платным публикациям.
          </p>
        </div>
      )}
    </section>
    </>
  );
}
