import type { KeyboardEvent } from "react";

import { TOPICS } from "../constants/topics";

interface PostFiltersProps {
  search: string;
  topic: string;
  onSearchChange: (value: string) => void;
  onTopicChange: (value: string) => void;
  onSearchSubmit: () => void;
}

export default function PostFilters({
  search,
  topic,
  onSearchChange,
  onTopicChange,
  onSearchSubmit,
}: PostFiltersProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      onSearchSubmit();
    }
  };

  return (
    <div className="post-filters">
      <div className="filter-search">
        <i className="fa-solid fa-magnifying-glass" aria-hidden="true" />
        <input
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Поиск по заголовку и тексту…"
          aria-label="Поиск публикаций"
        />
        <button type="button" className="filter-search-btn" onClick={onSearchSubmit}>
          Найти
        </button>
      </div>
      <select
        className="filter-select"
        value={topic}
        onChange={(event) => onTopicChange(event.target.value)}
        aria-label="Тематика"
      >
        <option value="">Все темы</option>
        {TOPICS.map((item) => (
          <option key={item.slug} value={item.slug}>
            {item.label}
          </option>
        ))}
      </select>
    </div>
  );
}
