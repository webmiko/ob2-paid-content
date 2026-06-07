"""PostView и счётчик просмотров публикаций."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0003_post_video_url_comment"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="view_count",
            field=models.PositiveIntegerField(default=0, verbose_name="Просмотры"),
        ),
        migrations.CreateModel(
            name="PostView",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ip_hash",
                    models.CharField(blank=True, default="", max_length=64, verbose_name="Хеш IP"),
                ),
                ("viewed_at", models.DateTimeField(auto_now_add=True, verbose_name="Когда")),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="views",
                        to="posts.post",
                        verbose_name="Публикация",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_views",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Читатель",
                    ),
                ),
            ],
            options={
                "verbose_name": "Просмотр публикации",
                "verbose_name_plural": "Просмотры публикаций",
                "ordering": ("-viewed_at",),
                "indexes": [
                    models.Index(fields=("post", "-viewed_at"), name="posts_postv_post_id_6f8b0d_idx"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="postview",
            constraint=models.UniqueConstraint(
                condition=models.Q(("user__isnull", False)),
                fields=("post", "user"),
                name="unique_post_view_user",
            ),
        ),
        migrations.AddConstraint(
            model_name="postview",
            constraint=models.UniqueConstraint(
                condition=models.Q(("user__isnull", True), ("ip_hash", ""), _negated=True),
                fields=("post", "ip_hash"),
                name="unique_post_view_ip",
            ),
        ),
    ]
