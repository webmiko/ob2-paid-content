"""SEO-поля публикаций."""

from django.db import migrations, models


def backfill_post_seo(apps, schema_editor) -> None:
    """Прописывает SEO для уже существующих публикаций."""
    Post = apps.get_model("posts", "Post")
    User = apps.get_model("users", "User")

    for post in Post.objects.select_related("author").iterator():
        author = post.author
        name = (getattr(author, "display_name", "") or "").strip()
        if name:
            author_label = name[:80]
        else:
            phone = getattr(author, "phone", "")
            author_label = f"Автор ·••{phone[-4:]}" if len(phone) >= 4 else f"Автор #{author.pk}"

        topic_labels = dict(
            [
                ("tech", "Технологии"),
                ("business", "Бизнес"),
                ("lifestyle", "Образ жизни"),
                ("education", "Образование"),
                ("creative", "Творчество"),
                ("other", "Другое"),
            ],
        )
        topic_label = topic_labels.get(post.topic, post.topic)
        meta_title = post.title[:70]

        body_text = (post.body or "").strip()
        if post.is_paid:
            meta_description = (
                f"Платная публикация «{post.title}» ({topic_label}) — {author_label}. "
                f"Подписка Creavity открывает доступ."
            )[:160]
        elif body_text:
            excerpt = body_text[:120]
            meta_description = f"{excerpt} — {author_label}, Creavity."[:160]
        else:
            meta_description = f"{post.title}. {topic_label} — {author_label} на Creavity."[:160]

        keywords = ", ".join(
            dict.fromkeys(
                [post.title, topic_label, author_label, "Creavity", "публикации", "авторы"]
                + (["платный контент"] if post.is_paid else []),
            ),
        )[:255]

        Post.objects.filter(pk=post.pk).update(
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=keywords,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0005_fix_postview_constraints"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="meta_description",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Meta description для поисковиков и Open Graph.",
                max_length=160,
                verbose_name="SEO описание",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="meta_keywords",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Keywords через запятую; генерируются автоматически.",
                max_length=255,
                verbose_name="SEO ключевые слова",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="meta_title",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Заполняется автоматически при сохранении.",
                max_length=70,
                verbose_name="SEO заголовок",
            ),
        ),
        migrations.RunPython(backfill_post_seo, migrations.RunPython.noop),
    ]
