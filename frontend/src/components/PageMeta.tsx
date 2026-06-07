import type { PageMetaOptions } from "../seo/usePageMeta";
import { usePageMeta } from "../seo/usePageMeta";

export type PageMetaProps = PageMetaOptions;

/** Компонент-обёртка для SEO meta-тегов на странице. */
export default function PageMeta(props: PageMetaProps) {
  usePageMeta(props);
  return null;
}
