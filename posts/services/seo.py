"""Генерация и синхронизация SEO-метаданных публикаций."""

from dataclasses import dataclass

from config.constants import META_DESCRIPTION_MAX, META_KEYWORDS_MAX, META_TITLE_MAX, SITE_NAME
from posts.models import Post
from users.services.display import get_public_author_label


@dataclass(frozen=True)
class PostSeoPayload:
    """Набор SEO-полей для одной публикации."""

    meta_title: str
    meta_description: str
    meta_keywords: str


def truncate_seo_text(text: str, max_length: int) -> str:
    """Обрезает текст до лимита meta-тегов с многоточием."""
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_length:
        return cleaned
    return f"{cleaned[: max_length - 1].rstrip()}…"


def build_post_seo(post: Post) -> PostSeoPayload:
    """Собирает title, description и keywords из данных публикации."""
    author_label = get_public_author_label(post.author)
    topic_label = post.get_topic_display()
    meta_title = truncate_seo_text(post.title, META_TITLE_MAX)

    body_text = (post.body or "").strip()
    if post.is_paid:
        meta_description = truncate_seo_text(
            f"Платная публикация «{post.title}» ({topic_label}) — {author_label}. "
            f"Подписка {SITE_NAME} открывает доступ.",
            META_DESCRIPTION_MAX,
        )
    elif body_text:
        excerpt = truncate_seo_text(body_text, META_DESCRIPTION_MAX - 40)
        meta_description = truncate_seo_text(
            f"{excerpt} — {author_label}, {SITE_NAME}.",
            META_DESCRIPTION_MAX,
        )
    else:
        meta_description = truncate_seo_text(
            f"{post.title}. {topic_label} — {author_label} на {SITE_NAME}.",
            META_DESCRIPTION_MAX,
        )

    keyword_parts = [
        post.title,
        topic_label,
        author_label,
        SITE_NAME,
        "публикации",
        "авторы",
    ]
    if post.is_paid:
        keyword_parts.append("платный контент")
    meta_keywords = truncate_seo_text(
        ", ".join(dict.fromkeys(keyword_parts)),
        META_KEYWORDS_MAX,
    )

    return PostSeoPayload(
        meta_title=meta_title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
    )


def sync_post_seo(post: Post) -> bool:
    """Записывает SEO-поля публикации при создании или изменении."""
    loaded = Post.objects.select_related("author").get(pk=post.pk)
    payload = build_post_seo(loaded)
    updates: dict[str, str] = {}

    if loaded.meta_title != payload.meta_title:
        updates["meta_title"] = payload.meta_title
    if loaded.meta_description != payload.meta_description:
        updates["meta_description"] = payload.meta_description
    if loaded.meta_keywords != payload.meta_keywords:
        updates["meta_keywords"] = payload.meta_keywords

    if not updates:
        return False

    Post.objects.filter(pk=loaded.pk).update(**updates)
    for field, value in updates.items():
        setattr(post, field, value)
    return True
