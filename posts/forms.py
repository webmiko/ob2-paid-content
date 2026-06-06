"""Формы редактирования публикаций в админке."""

from django import forms

from config.form_mixins import StyleFormMixin
from posts.models import Post


class PostAdminForm(StyleFormMixin, forms.ModelForm):
    """Форма редактирования публикации в админке."""

    class Meta:
        model = Post
        fields = ("title", "body", "is_paid", "author")
