"""URL-маршруты платежей."""

from django.urls import path

from users.payment_views import PaymentCreateView, PaymentDetailView, PaymentSuccessView

app_name = "payments"

urlpatterns = [
    path("create/", PaymentCreateView.as_view(), name="create"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("<int:payment_id>/", PaymentDetailView.as_view(), name="detail"),
]
