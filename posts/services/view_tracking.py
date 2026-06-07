"""Запись просмотров публикаций."""

import hashlib

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import F
from rest_framework.request import Request

from posts.models import Post, PostView


def get_client_ip(request: Request) -> str:
    """Возвращает IP клиента с учётом X-Forwarded-For."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def hash_client_ip(ip: str) -> str:
    """Хеширует IP для дедупликации гостевых просмотров."""
    return hashlib.sha256(ip.encode()).hexdigest()[:32]


def record_post_view(
    post: Post,
    request: Request,
) -> bool:
    """Сохраняет уникальный просмотр; просмотры автора своих постов не считаются.

    Returns:
        True, если просмотр записан впервые.
    """
    user = request.user
    if isinstance(user, AbstractBaseUser) and user.is_authenticated:
        if user.pk == post.author_id:
            return False
        _view, created = PostView.objects.get_or_create(post=post, user=user)
    else:
        ip = get_client_ip(request)
        if not ip:
            return False
        ip_hash = hash_client_ip(ip)
        _view, created = PostView.objects.get_or_create(
            post=post,
            user=None,
            ip_hash=ip_hash,
        )

    if created:
        Post.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)
    return created


def reader_type_for_view(user: AbstractBaseUser | AnonymousUser | None) -> str:
    """Тип читателя для ленты активности автора."""
    if user is None or not user.is_authenticated:
        return "guest"
    subscription = getattr(user, "subscription", None)
    if subscription is not None and subscription.is_active:
        return "subscriber"
    return "reader"
