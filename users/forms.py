"""Формы приложения users (admin и Django Forms)."""

from django import forms

from config.form_mixins import StyleFormMixin
from users.models import User
from users.validators import normalize_phone


class UserAdminForm(StyleFormMixin, forms.ModelForm):
    """Форма редактирования пользователя в Django admin."""

    class Meta:
        model = User
        fields = (
            "phone",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def clean_phone(self) -> str:
        """Нормализует телефон перед сохранением."""
        phone = self.cleaned_data["phone"]
        try:
            return normalize_phone(phone)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
