"""Django admin для users."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.forms import UserAdminForm
from users.models import Payment, Subscription, User


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админка платежей."""

    list_display = ("id", "user", "status", "amount", "currency", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("user__phone", "stripe_session_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ("user", "is_active", "activated_at", "payment")
    list_filter = ("is_active",)
    search_fields = ("user__phone",)
    readonly_fields = ("activated_at",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка пользователей с кастомной формой и полем phone."""

    form = UserAdminForm
    ordering = ("phone",)
    list_display = ("phone", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("phone", "first_name", "last_name", "email")

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Персональные данные", {"fields": ("first_name", "last_name", "email")}),
        (
            "Права",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
