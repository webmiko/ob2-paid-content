interface JsonLdProps {
  data: Record<string, unknown> | Record<string, unknown>[];
}

/** Вставляет JSON-LD для rich snippets поисковиков. */
export default function JsonLd({ data }: JsonLdProps) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
