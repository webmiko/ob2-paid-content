"""API-представления платежей и подписки."""

from typing import cast

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.throttling import PaymentRateThrottle, WebhookRateThrottle
from users.models import Payment, PaymentStatus, User
from users.payment_serializers import PaymentSerializer, PaymentSuccessSerializer
from users.services.access import user_has_active_subscription
from users.services.payment import (
    STRIPE_PAID_STATUS,
    PaymentValidationError,
    complete_paid_payment,
    validate_stripe_session_for_payment,
)
from users.services.stripe import StripeServiceError, create_checkout_session, retrieve_checkout_session
from users.services.subscription import activate_subscription

try:
    import stripe
except ImportError:  # pragma: no cover
    stripe = None  # type: ignore[assignment]


def _success_response(payment: Payment) -> Response:
    """Формирует ответ после успешного подтверждения оплаты."""
    subscription = activate_subscription(payment.pk)
    data = {"status": PaymentStatus.PAID, "subscription_active": subscription.is_active}
    return Response(PaymentSuccessSerializer(data).data)


def _confirm_payment_with_stripe(payment: Payment) -> Response:
    """Сверяет статус в Stripe и при оплате активирует подписку."""
    if payment.status == PaymentStatus.PAID:
        return _success_response(payment)

    if not payment.stripe_session_id:
        data = {"status": payment.status, "subscription_active": False}
        return Response(PaymentSuccessSerializer(data).data)

    try:
        session = retrieve_checkout_session(payment.stripe_session_id)
    except StripeServiceError:
        return Response(
            {"detail": "Payment service unavailable"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    try:
        validate_stripe_session_for_payment(session, payment)
    except PaymentValidationError:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if session.payment_status != STRIPE_PAID_STATUS:
        data = {"status": payment.status, "subscription_active": False}
        return Response(PaymentSuccessSerializer(data).data)

    complete_paid_payment(payment.pk)
    payment.refresh_from_db()
    return _success_response(payment)


class PaymentCreateView(APIView):
    """Создание Stripe Checkout для оплаты подписки."""

    permission_classes = (IsAuthenticated,)
    throttle_classes = (PaymentRateThrottle,)

    def post(self, request: Request) -> Response:
        """Создаёт Stripe Checkout или возвращает существующий PENDING url."""
        user = cast(User, request.user)

        with transaction.atomic():
            locked_user = User.objects.select_for_update().get(pk=user.pk)
            if user_has_active_subscription(locked_user):
                return Response(
                    {"detail": "Subscription already active."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            pending = (
                Payment.objects.filter(
                    user=locked_user,
                    status=PaymentStatus.PENDING,
                )
                .order_by("-created_at")
                .first()
            )

            if pending and pending.payment_url:
                return Response(PaymentSerializer(pending).data, status=status.HTTP_200_OK)

            if not pending:
                try:
                    pending = Payment.objects.create(
                        user=locked_user,
                        status=PaymentStatus.PENDING,
                        amount=settings.STRIPE_SUBSCRIPTION_AMOUNT,
                        currency=settings.STRIPE_CURRENCY,
                    )
                except IntegrityError:
                    pending = (
                        Payment.objects.filter(
                            user=locked_user,
                            status=PaymentStatus.PENDING,
                        )
                        .order_by("-created_at")
                        .first()
                    )
                    if pending and pending.payment_url:
                        return Response(PaymentSerializer(pending).data, status=status.HTTP_200_OK)
                    raise

            payment = pending

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
    """Подтверждение оплаты по session_id и активация подписки."""

    permission_classes = (IsAuthenticated,)
    throttle_classes = (PaymentRateThrottle,)

    def post(self, request: Request) -> Response:
        """Синхронизирует оплату в Stripe и активирует подписку."""
        session_id = request.data.get("session_id", "")
        if isinstance(session_id, str):
            session_id = session_id.strip()
        else:
            session_id = ""

        if not session_id:
            return Response({"session_id": ["Обязательное поле."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(stripe_session_id=session_id, user=cast(User, request.user))
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return _confirm_payment_with_stripe(payment)


class PaymentSyncView(APIView):
    """Синхронизация последнего ожидающего платежа пользователя со Stripe."""

    permission_classes = (IsAuthenticated,)
    throttle_classes = (PaymentRateThrottle,)

    def post(self, request: Request) -> Response:
        """Проверяет последний PENDING-платёж с session_id у Stripe."""
        user = cast(User, request.user)
        if user_has_active_subscription(user):
            data = {"status": PaymentStatus.PAID, "subscription_active": True}
            return Response(PaymentSuccessSerializer(data).data)

        payment = (
            Payment.objects.filter(
                user=user,
                status=PaymentStatus.PENDING,
                stripe_session_id__isnull=False,
            )
            .exclude(stripe_session_id="")
            .order_by("-created_at")
            .first()
        )
        if payment is None:
            data = {"status": PaymentStatus.PENDING, "subscription_active": False}
            return Response(PaymentSuccessSerializer(data).data)

        return _confirm_payment_with_stripe(payment)


class PaymentDetailView(APIView):
    """Просмотр статуса платежа владельцем."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, payment_id: int) -> Response:
        """Возвращает статус платежа владельцу."""
        try:
            payment = Payment.objects.get(pk=payment_id, user=cast(User, request.user))
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """Webhook Stripe checkout.session.completed."""

    permission_classes = (AllowAny,)
    authentication_classes: list = []
    throttle_classes = (WebhookRateThrottle,)

    def post(self, request: Request) -> Response:
        """Активирует подписку по событию Stripe без участия клиента."""
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        if not webhook_secret or stripe is None:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

        signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(request.body, signature, webhook_secret)
        except (ValueError, stripe.SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event["type"] != "checkout.session.completed":
            return Response({"received": True})

        session_object = event["data"]["object"]
        session_id = session_object.get("id")
        payment_status = session_object.get("payment_status")
        metadata = session_object.get("metadata") or {}
        payment_id_raw = metadata.get("payment_id")

        if payment_status != STRIPE_PAID_STATUS or not payment_id_raw:
            return Response({"received": True})

        try:
            payment = Payment.objects.get(pk=int(payment_id_raw), stripe_session_id=session_id)
        except (Payment.DoesNotExist, ValueError, TypeError):
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            session = retrieve_checkout_session(session_id)
            validate_stripe_session_for_payment(session, payment)
        except (StripeServiceError, PaymentValidationError):
            return Response(status=status.HTTP_404_NOT_FOUND)

        if payment.status != PaymentStatus.PAID:
            complete_paid_payment(payment.pk)

        return Response({"received": True})


def payment_success_page(request: HttpRequest) -> HttpResponse:
    """Страница «оплата успешна» после редиректа из Stripe."""
    return render(request, "payments/success.html")
