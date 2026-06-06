/** Тематики публикаций — синхронизированы с posts.choices.PostTopic. */

export interface TopicOption {
  slug: string;
  label: string;
}

export const TOPICS: TopicOption[] = [
  { slug: "tech", label: "Технологии" },
  { slug: "business", label: "Бизнес" },
  { slug: "lifestyle", label: "Образ жизни" },
  { slug: "education", label: "Образование" },
  { slug: "creative", label: "Творчество" },
  { slug: "other", label: "Другое" },
];

export function topicLabel(slug: string): string {
  return TOPICS.find((item) => item.slug === slug)?.label ?? slug;
}
