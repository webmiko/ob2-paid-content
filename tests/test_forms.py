"""Тесты Django-форм и StyleFormMixin."""

import pytest
from django import forms

from config.form_mixins import StyleFormMixin
from users.forms import UserAdminForm


class SampleForm(StyleFormMixin, forms.Form):
    """Тестовая форма для проверки mixin."""

    name = forms.CharField()
    active = forms.BooleanField(required=False)
    role = forms.ChoiceField(choices=(("a", "A"), ("b", "B")))


def test_style_form_mixin_applies_bootstrap_classes() -> None:
    """StyleFormMixin проставляет классы Bootstrap 5."""
    form = SampleForm()
    assert "form-control" in form.fields["name"].widget.attrs.get("class", "")
    assert "form-check-input" in form.fields["active"].widget.attrs.get("class", "")
    assert "form-select" in form.fields["role"].widget.attrs.get("class", "")


@pytest.mark.django_db
def test_user_admin_form_normalizes_phone(author) -> None:
    """UserAdminForm нормализует телефон в clean_phone."""
    form = UserAdminForm(data={"phone": "+7 900 111-22-33"}, instance=author)
    assert form.is_valid()
    assert form.cleaned_data["phone"] == "79001112233"


@pytest.mark.django_db
def test_user_admin_form_rejects_invalid_phone(author) -> None:
    """UserAdminForm отклоняет некорректный телефон."""
    form = UserAdminForm(data={"phone": "bad"}, instance=author)
    assert not form.is_valid()
    assert "phone" in form.errors
