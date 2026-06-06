"""Демо-курсы школы «Речь и ритм» — один автор, бесплатные и платные материалы."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from posts.models import Post
from users.models import User

if TYPE_CHECKING:
    from argparse import ArgumentParser

SPEECH_AUTHOR_PHONE = "79000002001"
SPEECH_AUTHOR_NAME = "Школа «Речь и ритм»"
SPEECH_DEMO_PASSWORD = "DemoPass123"


@dataclass(frozen=True)
class SpeechCourse:
    """Курс как публикация на платформе Creavity."""

    title: str
    body: str
    is_paid: bool
    days_ago: int
    video_url: str = ""


SPEECH_DEMO_VIDEO = "https://rutube.ru/video/c7858c15d841423bbec1000002307a76/"
SPEECH_INTRO_DZEN = "https://dzen.ru/video/watch/speech-rhythm-intro"
SPEECH_VK_LESSON = "https://vk.com/video-456239017_456239123"
SPEECH_VIMEO_TEEN = "https://vimeo.com/148751763"

SPEECH_COURSES: tuple[SpeechCourse, ...] = (
    SpeechCourse(
        title="Дыхание и голос: базовый курс",
        body=(
            "Фундамент перед любой программой: диафрагмальное дыхание, мягкий голосовой "
            "старт, паузы и связность фраз без перегруза видео.\n\n"
            "Аудитория: все возрасты · 4 недели · 15–20 минут в день.\n\n"
            "Бесплатный вводный модуль: короткий опрос, упражнения на дыхание и первые "
            "шаги к спокойному темпу речи."
        ),
        is_paid=False,
        days_ago=14,
        video_url=SPEECH_DEMO_VIDEO,
    ),
    SpeechCourse(
        title="Диагностика темпа: с чего начать",
        body=(
            "Короткий опрос и упражнения на дыхание — понимаем, где речь «спотыкается», "
            "и подбираем комфортный ритм без давления на результат.\n\n"
            "Бесплатный материал из блока «Как проходит обучение». Подходит перед "
            "выбором основной программы."
        ),
        is_paid=False,
        days_ago=13,
        video_url=SPEECH_INTRO_DZEN,
    ),
    SpeechCourse(
        title="Заикание у детей 4–7 лет: мягкий старт",
        body=(
            "Игровые упражнения, ритм речи и поддержка родителей. Курс для семей, "
            "которые хотят помочь ребёнку говорить спокойнее без давления.\n\n"
            "Аудитория: дети 4–7 лет · 8 недель · игровой формат, короткие сессии.\n\n"
            "Платный модуль: пошаговые занятия, домашние задания и рекомендации для "
            "родителей. Полный доступ — по подписке платформы Creavity."
        ),
        is_paid=True,
        days_ago=10,
        video_url=SPEECH_VK_LESSON,
    ),
    SpeechCourse(
        title="Речь подростка: уверенность и плавность",
        body=(
            "Работа с волнением перед ответами в школе, разговорами со сверстниками "
            "и выступлениями. Практики на каждый день.\n\n"
            "Аудитория: подростки 12–17 лет · 10 недель.\n\n"
            "Платный курс: сценарии для школы, у доски и в компании сверстников — "
            "без страха «застрять» на слове."
        ),
        is_paid=True,
        days_ago=9,
        video_url=SPEECH_VIMEO_TEEN,
    ),
    SpeechCourse(
        title="Взрослым: заикание в жизни и на работе",
        body=(
            "Стратегии для звонков, встреч и публичных ситуаций. Учимся снижать "
            "напряжение и строить речь от опоры, а не от спешки.\n\n"
            "Аудитория: взрослые 18+ · 12 недель.\n\n"
            "Платный курс: работа, переговоры, созвоны — спокойная речь там, "
            "где раньше нарастало напряжение."
        ),
        is_paid=True,
        days_ago=7,
    ),
    SpeechCourse(
        title="Домашние упражнения для всей семьи",
        body=(
            "Короткие сессии по 15–20 минут: дыхание, темп, чтение вслух и совместные "
            "ритуалы, которые закрепляют успех ребёнка дома.\n\n"
            "Аудитория: семьи · 6 недель.\n\n"
            "Платный курс: программа для дома, которую можно проходить вместе "
            "с ребёнком или подростком."
        ),
        is_paid=True,
        days_ago=5,
    ),
    SpeechCourse(
        title="Родителям: как поддерживать, не давить",
        body=(
            "Понятные правила общения, чего избегать, как реагировать на сложные "
            "моменты и когда обращаться к специалисту очно.\n\n"
            "Аудитория: родители · 5 недель.\n\n"
            "Платный курс: поддержка дома без давления на «идеальную» дикцию — "
            "внимание к эмоциям и ритму речи."
        ),
        is_paid=True,
        days_ago=3,
    ),
)


class Command(BaseCommand):
    """Загружает курсы школы «Речь и ритм» одним автором."""

    help = (
        "Создаёт автора «Речь и ритм» и публикации-курсы "
        "(2 бесплатных, 5 платных) по мотивам rech-i-ritm."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Флаг пересоздания публикаций автора."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Удалить старые публикации автора и создать заново.",
        )

    def handle(self, *args: object, **options: object) -> None:
        """Создаёт или обновляет курсы в базе."""
        force = bool(options.get("force"))
        now = timezone.now()

        with transaction.atomic():
            author, created = User.objects.get_or_create(
                phone=SPEECH_AUTHOR_PHONE,
                defaults={"display_name": SPEECH_AUTHOR_NAME},
            )
            if author.display_name != SPEECH_AUTHOR_NAME:
                author.display_name = SPEECH_AUTHOR_NAME
                author.save(update_fields=["display_name"])
            if created:
                author.set_password(SPEECH_DEMO_PASSWORD)
                author.save(update_fields=["password"])

            if force:
                deleted, _ = Post.objects.filter(author=author).delete()
                self.stdout.write(f"Удалено публикаций автора: {deleted}")

            created_count = 0
            for course in SPEECH_COURSES:
                exists = Post.objects.filter(author=author, title=course.title).exists()
                if exists and not force:
                    continue
                Post.objects.update_or_create(
                    author=author,
                    title=course.title,
                    defaults={
                        "body": course.body,
                        "is_paid": course.is_paid,
                        "topic": "education",
                        "video_url": course.video_url,
                        "created_at": now - timezone.timedelta(days=course.days_ago),
                    },
                )
                created_count += 1

        free_count = sum(1 for c in SPEECH_COURSES if not c.is_paid)
        paid_count = sum(1 for c in SPEECH_COURSES if c.is_paid)
        self.stdout.write(
            self.style.SUCCESS(
                f"Курсы «Речь и ритм» готовы: {created_count} публикаций "
                f"({free_count} бесплатных, {paid_count} платных).",
            ),
        )
        self.stdout.write(f"Автор: {SPEECH_AUTHOR_NAME}, телефон {SPEECH_AUTHOR_PHONE}")
        self.stdout.write(f"Пароль: {SPEECH_DEMO_PASSWORD}")
