"""Тесты SEO: sitemap и robots."""

import pytest
from django.test import override_settings
from rest_framework import status

from posts.models import Post


@pytest.mark.django_db
@override_settings(SITE_URL="https://creavity.example")
def test_sitemap_xml_lists_public_urls(api_client, free_post, author) -> None:
    """sitemap.xml содержит главную, темы, посты и авторов."""
    response = api_client.get("/sitemap.xml")
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"].startswith("application/xml")
    body = response.content.decode()
    assert "https://creavity.example/" in body
    assert "https://creavity.example/explore" in body
    assert f"https://creavity.example/posts/{free_post.pk}" in body
    assert f"https://creavity.example/authors/{author.pk}" in body
    assert "https://creavity.example/topics/tech" in body


@pytest.mark.django_db
@override_settings(SITE_URL="https://creavity.example")
def test_robots_txt_disallows_private_paths(api_client) -> None:
    """robots.txt закрывает личные разделы и указывает sitemap."""
    response = api_client.get("/robots.txt")
    assert response.status_code == status.HTTP_200_OK
    body = response.content.decode()
    assert "Disallow: /profile" in body
    assert "Disallow: /login" in body
    assert "Sitemap: https://creavity.example/sitemap.xml" in body


@pytest.mark.django_db
@override_settings(SITE_URL="https://creavity.example")
def test_llms_txt_has_h1_and_links(api_client) -> None:
    """llms.txt в Markdown: заголовок H1 и ссылки на разделы сайта."""
    response = api_client.get("/llms.txt")
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"].startswith("text/plain")
    body = response.content.decode()
    assert body.startswith("# Creavity")
    assert "[Лента](https://creavity.example/)" in body
    assert "[Sitemap](https://creavity.example/sitemap.xml)" in body
    assert "github.com/webmiko/ob2-paid-content" in body


@pytest.mark.django_db
@override_settings(SITE_URL="https://creavity.example")
def test_sitemap_respects_post_limit(api_client, author) -> None:
    """Sitemap не раздувается сверх лимита постов."""
    for index in range(3):
        Post.objects.create(title=f"P {index}", body="B", author=author)
    response = api_client.get("/sitemap.xml")
    assert response.status_code == status.HTTP_200_OK
    assert response.content.decode().count("<url>") >= 5
