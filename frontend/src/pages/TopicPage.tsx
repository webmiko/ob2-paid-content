import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import ContentTypeTabs from "../components/ContentTypeTabs";
import JsonLd from "../components/JsonLd";
import PageMeta from "../components/PageMeta";
import PostListSection from "../components/PostListSection";
import { topicLabel } from "../constants/topics";
import { usePostsList } from "../hooks/usePostsList";
import { absoluteUrl } from "../seo/site";
import "../styles/deferred/explore.css";

export default function TopicPage() {
  const { slug } = useParams();
  const [content, setContent] = useState<"all" | "free" | "paid" | "available">("all");

  const filters = useMemo(
    () => ({
      content,
      topic: slug,
    }),
    [content, slug],
  );
  const { posts, error, loading, loadingMore, nextPath, loadMore } = usePostsList(filters);

  const label = slug ? topicLabel(slug) : "Тема";
  const topicPath = slug ? `/topics/${slug}` : "/explore";

  return (
    <>
      <PageMeta
        title={`Тема: ${label}`}
        description={`Публикации Creavity по теме «${label}»: бесплатные и платные материалы авторов.`}
        path={topicPath}
      />
      {slug && (
        <JsonLd
          data={{
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: label,
            url: absoluteUrl(topicPath),
            description: `Публикации Creavity по теме «${label}».`,
            inLanguage: "ru-RU",
          }}
        />
      )}
      <section>
      <Link className="back-link" to="/explore">
        ← К каталогу
      </Link>
      <div className="card author-header">
        <div className="author-header-icon topic-icon">
          <i className="fa-solid fa-hashtag" aria-hidden="true" />
        </div>
        <div>
          <h1 className="page-title">{label}</h1>
          <p className="page-subtitle mb-0">Публикации по теме «{label}»</p>
        </div>
      </div>

      <ContentTypeTabs value={content} onChange={setContent} />

      <PostListSection
        posts={posts}
        error={error}
        loading={loading}
        loadingMore={loadingMore}
        nextPath={nextPath}
        onLoadMore={() => void loadMore()}
        emptyTitle="В этой теме пока нет публикаций"
      />
    </section>
    </>
  );
}
