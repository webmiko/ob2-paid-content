"""Тематика публикации для фильтрации и поиска."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="topic",
            field=models.CharField(
                choices=[
                    ("tech", "Технологии"),
                    ("business", "Бизнес"),
                    ("lifestyle", "Образ жизни"),
                    ("education", "Образование"),
                    ("creative", "Творчество"),
                    ("other", "Другое"),
                ],
                default="other",
                max_length=32,
                verbose_name="Тематика",
            ),
        ),
    ]
