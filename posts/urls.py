"""URL-маршруты posts."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from posts.comment_views import (
    PostCommentDetailView,
    PostCommentListCreateView,
    RecommendedPostsView,
    SimilarPostsView,
)
from posts.meta_views import AuthorDetailView, AuthorListView, TopicListView
from posts.view_views import PostRecordViewView
from posts.views import PostViewSet

router = DefaultRouter()
router.register("", PostViewSet, basename="post")

app_name = "posts"

urlpatterns = [
    path("recommended/", RecommendedPostsView.as_view(), name="recommended"),
    path("authors/", AuthorListView.as_view(), name="author-list"),
    path("authors/<int:author_id>/", AuthorDetailView.as_view(), name="author-detail"),
    path("topics/", TopicListView.as_view(), name="topic-list"),
    path("<int:post_id>/similar/", SimilarPostsView.as_view(), name="post-similar"),
    path("<int:post_id>/view/", PostRecordViewView.as_view(), name="post-view"),
    path("<int:post_id>/comments/", PostCommentListCreateView.as_view(), name="post-comments"),
    path(
        "<int:post_id>/comments/<int:comment_id>/",
        PostCommentDetailView.as_view(),
        name="post-comment-detail",
    ),
    path("", include(router.urls)),
]
