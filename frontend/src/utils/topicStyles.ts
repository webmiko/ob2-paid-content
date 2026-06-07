/** CSS-модификатор фона карточки по тематике публикации. */

const TOPIC_CARD_CLASSES = new Set([
  "post-card--topic-tech",
  "post-card--topic-business",
  "post-card--topic-lifestyle",
  "post-card--topic-education",
  "post-card--topic-creative",
  "post-card--topic-other",
]);

export function topicCardClassName(topic: string, baseClass = "card post-card"): string {
  const modifier = TOPIC_CARD_CLASSES.has(`post-card--topic-${topic}`)
    ? `post-card--topic-${topic}`
    : "post-card--topic-other";
  return `${baseClass} ${modifier}`;
}
