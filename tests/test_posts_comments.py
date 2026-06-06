"""Тесты API комментариев к публикациям."""

import pytest
from rest_framework import status

from posts.models import Comment
from tests.conftest import post_comment_detail_url, post_comments_url


@pytest.mark.django_db
def test_guest_can_list_comments_on_free_post(api_client, free_post, other_user) -> None:
    """Guest читает комментарии к бесплатной публикации."""
    Comment.objects.create(post=free_post, author=other_user, text="Полезно!")
    response = api_client.get(post_comments_url(free_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["text"] == "Полезно!"
    assert "can_delete" in response.data["results"][0]


@pytest.mark.django_db
def test_guest_cannot_list_comments_on_paid_post(api_client, paid_post, other_user) -> None:
    """Guest получает 403 при попытке читать комментарии к paid без доступа."""
    Comment.objects.create(post=paid_post, author=other_user, text="Hidden thread")
    response = api_client.get(post_comments_url(paid_post.pk))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_auth_user_creates_comment_on_free_post(other_auth_client, free_post, other_user) -> None:
    """Авторизованный пользователь оставляет комментарий."""
    response = other_auth_client.post(
        post_comments_url(free_post.pk),
        {"text": "  Спасибо за материал  "},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["text"] == "Спасибо за материал"
    assert response.data["author_id"] == other_user.pk
    assert response.data["can_delete"] is True


@pytest.mark.django_db
def test_author_can_delete_comment_on_own_post(auth_client, free_post, other_user) -> None:
    """Автор публикации может удалить чужой комментарий."""
    comment = Comment.objects.create(post=free_post, author=other_user, text="Remove me")
    response = auth_client.delete(post_comment_detail_url(free_post.pk, comment.pk))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_user_deletes_own_comment(other_auth_client, free_post, other_user) -> None:
    """Автор комментария удаляет свой комментарий."""
    comment = Comment.objects.create(post=free_post, author=other_user, text="Mine")
    response = other_auth_client.delete(post_comment_detail_url(free_post.pk, comment.pk))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_cannot_delete_others_comment(other_auth_client, free_post, author) -> None:
    """Пользователь не может удалить чужой комментарий на чужом посте."""
    comment = Comment.objects.create(post=free_post, author=author, text="Authors comment")
    response = other_auth_client.delete(post_comment_detail_url(free_post.pk, comment.pk))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_comments_pagination(api_client, free_post, other_user) -> None:
    """Комментарии отдаются постранично."""
    for index in range(25):
        Comment.objects.create(post=free_post, author=other_user, text=f"Comment {index}")
    response = api_client.get(post_comments_url(free_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 25
    assert len(response.data["results"]) == 20
    assert response.data["next"] is not None


@pytest.mark.django_db
def test_empty_comment_rejected(other_auth_client, free_post) -> None:
    """Пустой комментарий отклоняется валидацией."""
    response = other_auth_client.post(
        post_comments_url(free_post.pk),
        {"text": "   "},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
