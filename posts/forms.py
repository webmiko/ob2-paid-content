"""Формы posts для Django admin."""

from django import forms

from config.form_mixins import StyleFormMixin
from posts.models import Post


class PostAdminForm(StyleFormMixin, forms.ModelForm):
    """Форма редактирования публикации в Django admin."""

    class Meta:
        model = Post
        fields = ("title", "body", "is_paid", "author")
