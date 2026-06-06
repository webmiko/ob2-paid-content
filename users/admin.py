"""Django admin для users."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.forms import UserAdminForm
from users.models import User


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
