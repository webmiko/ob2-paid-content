"""API-представления платежей и подписки."""

from typing import cast

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Payment, PaymentStatus, User
from users.payment_serializers import PaymentSerializer, PaymentSuccessSerializer
from users.services.stripe import StripeServiceError, create_checkout_session, retrieve_checkout_session
from users.services.subscription import activate_subscription

STRIPE_PAID_STATUS = "paid"


class PaymentCreateView(APIView):
    """POST /api/payments/create/ — создаёт или возвращает PENDING Checkout."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """Создаёт Stripe Checkout или возвращает существующий PENDING url."""
        user = cast(User, request.user)
        pending = (
            Payment.objects.filter(
                user=user,
                status=PaymentStatus.PENDING,
            )
            .order_by("-created_at")
            .first()
        )

        if pending and pending.payment_url:
            return Response(PaymentSerializer(pending).data, status=status.HTTP_200_OK)

        payment = pending or Payment.objects.create(
            user=user,
            status=PaymentStatus.PENDING,
            amount=settings.STRIPE_SUBSCRIPTION_AMOUNT,
            currency=settings.STRIPE_CURRENCY,
        )

        try:
            session = create_checkout_session(payment)
        except StripeServiceError:
            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=["status", "updated_at"])
            return Response(
                {"detail": "Payment service unavailable"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payment.stripe_session_id = session.session_id
        payment.payment_url = session.payment_url
        payment.save(update_fields=["stripe_session_id", "payment_url", "updated_at"])
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentSuccessView(APIView):
    """GET /api/payments/success/?session_id= — sync Stripe и activate_subscription."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """Проверяет session_id в Stripe и активирует подписку."""
        session_id = request.query_params.get("session_id", "").strip()
        if not session_id:
            return Response({"session_id": ["Обязательный параметр."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(stripe_session_id=session_id, user=cast(User, request.user))
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if payment.status == PaymentStatus.PAID:
            subscription_active = activate_subscription(payment.pk).is_active
            data = {"status": PaymentStatus.PAID, "subscription_active": subscription_active}
            return Response(PaymentSuccessSerializer(data).data)

        try:
            session = retrieve_checkout_session(session_id)
        except StripeServiceError:
            return Response(
                {"detail": "Payment service unavailable"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if session.payment_status != STRIPE_PAID_STATUS:
            data = {"status": payment.status, "subscription_active": False}
            return Response(PaymentSuccessSerializer(data).data)

        payment.status = PaymentStatus.PAID
        payment.save(update_fields=["status", "updated_at"])
        subscription = activate_subscription(payment.pk)
        data = {"status": PaymentStatus.PAID, "subscription_active": subscription.is_active}
        return Response(PaymentSuccessSerializer(data).data)


class PaymentDetailView(APIView):
    """GET /api/payments/<id>/ — статус своего платежа."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, payment_id: int) -> Response:
        """Возвращает платёж только владельцу; чужой → 404."""
        try:
            payment = Payment.objects.get(pk=payment_id, user=cast(User, request.user))
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)


def payment_success_page(request: HttpRequest) -> HttpResponse:
    """Страница после редиректа Stripe (тег Templates)."""
    return render(request, "payments/success.html")
