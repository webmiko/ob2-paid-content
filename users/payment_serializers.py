"""Сериализаторы платежей и подписок."""

from rest_framework import serializers

from users.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Публичное представление платежа без stripe_* полей."""

    class Meta:
        model = Payment
        fields = ("id", "status", "payment_url", "amount", "currency", "created_at")
        read_only_fields = fields


class PaymentSuccessSerializer(serializers.Serializer):
    """Ответ после успешной синхронизации оплаты."""

    status = serializers.CharField()
    subscription_active = serializers.BooleanField()
