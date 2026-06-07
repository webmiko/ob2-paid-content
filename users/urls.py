"""URL-маршруты приложения users."""

from django.urls import path

from users.stats_views import AuthorStatsView
from users.views import PhoneSendCodeView, RegisterView, UserMeView

app_name = "users"

urlpatterns = [
    path("phone/send-code/", PhoneSendCodeView.as_view(), name="phone-send-code"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/stats/", AuthorStatsView.as_view(), name="me-stats"),
    path("me/", UserMeView.as_view(), name="me"),
]
