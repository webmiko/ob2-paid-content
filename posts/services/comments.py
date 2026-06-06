"""Права доступа к комментариям."""

from django.contrib.auth.models import AbstractBaseUser

from posts.models import Comment, Post


def can_delete_comment(user: AbstractBaseUser, comment: Comment, post: Post) -> bool:
    """Может ли пользователь удалить комментарий.

    Разрешено автору комментария, автору публикации и staff.
    """
    if user.is_staff:
        return True
    if comment.author_id == user.pk:
        return True
    return post.author_id == user.pk
