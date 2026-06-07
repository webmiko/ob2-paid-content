/** CSS-модификатор цвета тега тематики (бывшие фоны карточек). */

const TOPIC_SLUGS = new Set([
  "tech",
  "business",
  "lifestyle",
  "education",
  "creative",
  "other",
]);

function topicSlug(topic: string): string {
  return TOPIC_SLUGS.has(topic) ? topic : "other";
}

export function topicChipClassName(topic: string, extra = ""): string {
  const slug = topicSlug(topic);
  const base = `topic-chip topic-chip--topic-${slug}`;
  return extra ? `${base} ${extra}` : base;
}
