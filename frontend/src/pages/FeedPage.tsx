import { useMemo, useState } from "react";

import ContentTypeTabs from "../components/ContentTypeTabs";
import JsonLd from "../components/JsonLd";
import PageMeta from "../components/PageMeta";
import PostFilters from "../components/PostFilters";
import PostListSection from "../components/PostListSection";
import { useAuth } from "../context/AuthContext";
import { usePostsList } from "../hooks/usePostsList";
import { DEFAULT_DESCRIPTION, getSiteUrl, SITE_NAME } from "../seo/site";

export default function FeedPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [content, setContent] = useState<"all" | "free" | "paid" | "available">("all");
  const [topic, setTopic] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");

  const filters = useMemo(
    () => ({ content, topic: topic || undefined, search: search || undefined }),
    [content, topic, search],
  );
  const { posts, error, loading, loadingMore, nextPath, loadMore } = usePostsList(filters);

  const applySearch = () => {
    setSearch(searchInput);
  };

  return (
    <>
      <PageMeta title={SITE_NAME} description={DEFAULT_DESCRIPTION} path="/" />
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "WebSite",
          name: SITE_NAME,
          url: getSiteUrl(),
          description: DEFAULT_DESCRIPTION,
          inLanguage: "ru-RU",
          publisher: {
            "@type": "Organization",
            name: SITE_NAME,
            url: getSiteUrl(),
          },
        }}
      />
      <section>
      <div className="page-header-row">
        <h1 className="page-title">
          <i className="fa-solid fa-stream" aria-hidden="true" /> Лента
        </h1>
        <p className="page-subtitle">
          Все публикации платформы. Платный контент открывается одной подпиской на Creavity.
        </p>
      </div>

      <ContentTypeTabs
        value={content}
        onChange={setContent}
        showAvailable={isAuthenticated && !authLoading}
      />

      <PostFilters
        search={searchInput}
        topic={topic}
        onSearchChange={setSearchInput}
        onTopicChange={setTopic}
        onSearchSubmit={applySearch}
      />

      <PostListSection
        posts={posts}
        error={error}
        loading={loading}
        loadingMore={loadingMore}
        nextPath={nextPath}
        onLoadMore={() => void loadMore()}
        emptyTitle="В ленте пока пусто"
        emptyText="Смените фильтры или создайте первую публикацию в профиле"
      />
    </section>
    </>
  );
}
