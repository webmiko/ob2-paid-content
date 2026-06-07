"""Публичное имя автора для ленты."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_payment_unique_pending_per_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="display_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Отображается в ленте вместо маскированного телефона.",
                max_length=80,
                verbose_name="Публичное имя",
            ),
        ),
    ]
