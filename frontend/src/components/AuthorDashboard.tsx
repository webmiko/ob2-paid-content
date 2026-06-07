/** Дашборд автора в профиле. */

import { Link } from "react-router-dom";

import type { AuthorDashboardStats } from "../api/types";
import PostBadge from "./PostBadge";
import { formatPostDate } from "../utils/avatar";

const READER_LABELS: Record<string, string> = {
  guest: "Гость",
  reader: "Читатель",
  subscriber: "Подписчик",
};

interface AuthorDashboardProps {
  stats: AuthorDashboardStats;
}

export default function AuthorDashboard({ stats }: AuthorDashboardProps) {
  return (
    <section className="author-dashboard">
      <h2 className="section-title">
        <i className="fa-solid fa-chart-line" aria-hidden="true" /> Статистика автора
      </h2>
      <p className="hint-text dashboard-hint">
        Подписка на Creavity общая для всей платформы — ниже аудитория платформы и
        вовлечённость в ваши материалы.
      </p>

      <div className="dashboard-stats-grid">
        <div className="dashboard-stat-card">
          <span className="dashboard-stat-value">{stats.total_views}</span>
          <span className="dashboard-stat-label">Просмотров</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="dashboard-stat-value">{stats.unique_readers}</span>
          <span className="dashboard-stat-label">Уникальных читателей</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="dashboard-stat-value">{stats.total_comments}</span>
          <span className="dashboard-stat-label">Комментариев</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="dashboard-stat-value">{stats.platform_subscribers}</span>
          <span className="dashboard-stat-label">Подписчиков платформы</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="dashboard-stat-value">{stats.subscribers_who_viewed}</span>
          <span className="dashboard-stat-label">Подписчиков читали вас</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="dashboard-stat-value">{stats.post_count}</span>
          <span className="dashboard-stat-label">
            Публикаций ({stats.free_count} беспл. / {stats.paid_count} платн.)
          </span>
        </div>
      </div>

      {stats.by_topic.length > 0 && (
        <div className="card dashboard-panel">
          <h3 className="dashboard-panel-title">По тематикам</h3>
          <div className="dashboard-table-wrap">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Тема</th>
                  <th>Посты</th>
                  <th>Просмотры</th>
                  <th>Комментарии</th>
                </tr>
              </thead>
              <tbody>
                {stats.by_topic.map((row) => (
                  <tr key={row.slug}>
                    <td>{row.label}</td>
                    <td>{row.post_count}</td>
                    <td>{row.views}</td>
                    <td>{row.comments}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {stats.top_posts.length > 0 && (
        <div className="card dashboard-panel">
          <h3 className="dashboard-panel-title">Топ по просмотрам</h3>
          <ul className="dashboard-top-list">
            {stats.top_posts.map((post, index) => (
              <li key={post.id}>
                <span className="dashboard-rank">{index + 1}</span>
                <div className="dashboard-top-body">
                  <Link to={`/posts/${post.id}`} className="text-link">
                    {post.title}
                  </Link>
                  <span className="dashboard-top-meta">
                    {post.view_count} просм. · {post.comment_count} комм.
                  </span>
                </div>
                <PostBadge isPaid={post.is_paid} />
              </li>
            ))}
          </ul>
        </div>
      )}

      {stats.recent_views.length > 0 && (
        <div className="card dashboard-panel">
          <h3 className="dashboard-panel-title">Недавние просмотры</h3>
          <ul className="dashboard-activity-list">
            {stats.recent_views.map((item) => (
              <li key={`${item.post_id}-${item.viewed_at}`}>
                <span className={`reader-chip reader-chip-${item.reader_type}`}>
                  {READER_LABELS[item.reader_type] ?? item.reader_type}
                </span>
                <Link to={`/posts/${item.post_id}`} className="text-link">
                  {item.post_title}
                </Link>
                <span className="dashboard-activity-time">{formatPostDate(item.viewed_at)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {stats.post_stats.length > 0 && (
        <div className="card dashboard-panel">
          <h3 className="dashboard-panel-title">Все публикации</h3>
          <div className="dashboard-table-wrap">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Заголовок</th>
                  <th>Тип</th>
                  <th>Просмотры</th>
                  <th>Комментарии</th>
                  <th>Дата</th>
                </tr>
              </thead>
              <tbody>
                {stats.post_stats.map((post) => (
                  <tr key={post.id}>
                    <td>
                      <Link to={`/posts/${post.id}`} className="text-link">
                        {post.title}
                      </Link>
                    </td>
                    <td>{post.is_paid ? "Платная" : "Бесплатная"}</td>
                    <td>{post.view_count}</td>
                    <td>{post.comment_count}</td>
                    <td>{formatPostDate(post.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
