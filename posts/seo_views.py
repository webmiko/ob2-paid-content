"""XML sitemap и robots для SEO."""

from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.utils.timezone import localtime

from posts.choices import PostTopic
from posts.models import Post

User = get_user_model()

SITEMAP_MAX_POSTS = 5000
SITEMAP_MAX_AUTHORS = 1000


def _format_lastmod(value: datetime | None) -> str:
    """Форматирует datetime в W3C для sitemap."""
    if value is None:
        return ""
    return localtime(value).strftime("%Y-%m-%d")


def _url_entry(loc: str, *, lastmod: str = "", changefreq: str = "weekly", priority: str = "0.5") -> str:
    """Одна запись url в sitemap."""
    lines = ["  <url>", f"    <loc>{loc}</loc>"]
    if lastmod:
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.extend(
        [
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ],
    )
    return "\n".join(lines)


def sitemap_xml_view(_request: HttpRequest) -> HttpResponse:
    """Публичный sitemap.xml с основными URL и публикациями."""
    base = settings.SITE_URL.rstrip("/")
    entries: list[str] = [
        _url_entry(f"{base}/", changefreq="daily", priority="1.0"),
        _url_entry(f"{base}/explore", changefreq="daily", priority="0.9"),
    ]

    for slug, _label in PostTopic.choices:
        entries.append(_url_entry(f"{base}/topics/{slug}", changefreq="weekly", priority="0.7"))

    posts = Post.objects.only("pk", "updated_at").order_by("-updated_at")[:SITEMAP_MAX_POSTS]
    for post in posts:
        lastmod = _format_lastmod(post.updated_at)
        entries.append(
            _url_entry(
                f"{base}/posts/{post.pk}",
                lastmod=lastmod,
                changefreq="weekly",
                priority="0.8",
            ),
        )

    authors = User.objects.filter(posts__isnull=False).distinct().order_by("-id")[:SITEMAP_MAX_AUTHORS]
    for author in authors:
        entries.append(
            _url_entry(
                f"{base}/authors/{author.pk}",
                changefreq="weekly",
                priority="0.6",
            ),
        )

    body = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            *entries,
            "</urlset>",
        ],
    )
    return HttpResponse(body, content_type="application/xml; charset=utf-8")


def robots_txt_view(_request: HttpRequest) -> HttpResponse:
    """Динамический robots.txt с абсолютным URL sitemap."""
    base = settings.SITE_URL.rstrip("/")
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /profile",
            "Disallow: /login",
            "Disallow: /register",
            "Disallow: /payment/",
            "",
            f"Sitemap: {base}/sitemap.xml",
            "",
        ],
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


def llms_txt_view(_request: HttpRequest) -> HttpResponse:
    """llms.txt — краткое описание сайта и ссылки для LLM-агентов (формат Markdown)."""
    base = settings.SITE_URL.rstrip("/")
    body = "\n".join(
        [
            "# Creavity",
            "",
            "> Платформа авторов: бесплатные публикации для всех, платный контент по одной подписке на всю платформу.",
            "",
            "Публичный веб-сайт (React SPA) и REST API (Django). "
            "Индексируйте ленту, каталог, темы, посты и профили авторов. "
            "Личный кабинет, регистрация и оплата — не для обучения моделей.",
            "",
            "## Основные страницы",
            "",
            f"- [Лента]({base}/): все публикации платформы",
            f"- [Каталог]({base}/explore): обзор контента по разделам",
            f"- [Пример темы «Технологии»]({base}/topics/tech): посты по теме",
            "",
            "## SEO и API",
            "",
            f"- [Sitemap]({base}/sitemap.xml): карта публичных URL",
            f"- [Robots.txt]({base}/robots.txt): правила обхода",
            f"- [Health check]({base}/api/health/): статус backend-сервиса",
            f"- [Список постов (JSON)]({base}/api/posts/): публичный REST API",
            "",
            "## Исходный код",
            "",
            "- [GitHub: ob2-paid-content](https://github.com/webmiko/ob2-paid-content): "
            "монорепозиторий Django + React",
            "",
            "## Ограничения",
            "",
            "- Тело платного поста доступно только подписчикам; не выводите paywall-контент без авторизации.",
            "- Не используйте `/login`, `/register`, `/profile`, `/payment/` как обучающие данные.",
            "",
        ],
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")
