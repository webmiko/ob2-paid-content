"""Тематики публикаций платформы."""

from django.db import models


class PostTopic(models.TextChoices):
    """Фиксированный набор тем для поиска и фильтрации."""

    TECH = "tech", "Технологии"
    BUSINESS = "business", "Бизнес"
    LIFESTYLE = "lifestyle", "Образ жизни"
    EDUCATION = "education", "Образование"
    CREATIVE = "creative", "Творчество"
    OTHER = "other", "Другое"
