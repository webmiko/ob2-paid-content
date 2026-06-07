"""URL-маршруты платежей."""

from django.urls import path

from users.payment_views import (
    PaymentCreateView,
    PaymentDetailView,
    PaymentSuccessView,
    PaymentSyncView,
    StripeWebhookView,
)

app_name = "payments"

urlpatterns = [
    path("create/", PaymentCreateView.as_view(), name="create"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("sync/", PaymentSyncView.as_view(), name="sync"),
    path("webhook/", StripeWebhookView.as_view(), name="webhook"),
    path("<int:payment_id>/", PaymentDetailView.as_view(), name="detail"),
]
