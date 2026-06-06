"""URL-маршруты приложения users."""

from django.urls import path

from users.views import RegisterView, UserMeView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", UserMeView.as_view(), name="me"),
]
