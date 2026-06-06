import type { ContentFilter } from "../hooks/usePostsList";

interface ContentTypeTabsProps {
  value: ContentFilter;
  onChange: (value: ContentFilter) => void;
  showAvailable?: boolean;
}

const TABS: { value: ContentFilter; label: string; icon: string }[] = [
  { value: "all", label: "Все", icon: "fa-layer-group" },
  { value: "free", label: "Бесплатные", icon: "fa-unlock" },
  { value: "paid", label: "Платные", icon: "fa-crown" },
  { value: "available", label: "Доступно мне", icon: "fa-eye" },
];

export default function ContentTypeTabs({
  value,
  onChange,
  showAvailable = true,
}: ContentTypeTabsProps) {
  const tabs = showAvailable ? TABS : TABS.filter((tab) => tab.value !== "available");

  return (
    <div className="content-tabs" role="tablist" aria-label="Тип контента">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          type="button"
          role="tab"
          aria-selected={value === tab.value}
          className={`content-tab${value === tab.value ? " active" : ""}`}
          onClick={() => onChange(tab.value)}
        >
          <i className={`fa-solid ${tab.icon}`} aria-hidden="true" /> {tab.label}
        </button>
      ))}
    </div>
  );
}
