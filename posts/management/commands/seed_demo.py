"""Загрузка демо-авторов и публикаций для локальной проверки UI."""

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

DEMO_PASSWORD = "DemoPass123"
DEMO_PHONE_PREFIX = "79000001"


@dataclass(frozen=True)
class DemoAuthor:
    """Автор демо-контента."""

    phone: str
    display_name: str


@dataclass(frozen=True)
class DemoPost:
    """Публикация демо-контента."""

    author_phone: str
    title: str
    body: str
    is_paid: bool
    topic: str
    days_ago: int
    video_url: str = ""


DEMO_VIDEO = "https://www.youtube.com/watch?v=aircAruvnKk"
DEMO_VIMEO = "https://vimeo.com/148751763"
DEMO_RUTUBE = "https://rutube.ru/video/c7858c15d841423bbec1000002307a76/"
DEMO_VK = "https://vk.com/video-456239017_456239123"
DEMO_DZEN = "https://dzen.ru/video/watch/creavity-art-intro"


DEMO_AUTHORS: tuple[DemoAuthor, ...] = (
    DemoAuthor("79000001001", "Алексей Смирнов"),
    DemoAuthor("79000001002", "Мария Петрова"),
    DemoAuthor("79000001003", "Иван Крылов"),
    DemoAuthor("79000001004", "Елена Виноградова"),
    DemoAuthor("79000001005", "Дмитрий Орлов"),
    DemoAuthor("79000001006", "София Назарова"),
)

DEMO_POSTS: tuple[DemoPost, ...] = (
    DemoPost(
        "79000001002",
        "Мастер-класс: рисуем маслом",
        "Бесплатный урок по технике мазка. Разбираем палитру, фактуру и базовый мазок на простом натюрморте.",
        False,
        "creative",
        5,
        video_url=DEMO_VIDEO,
    ),
    DemoPost(
        "79000001002",
        "Секреты композиции",
        "Как сделать кадр живым? Делимся лайфхаками: правило третей, контраст массы и точки фокуса.",
        False,
        "creative",
        4,
    ),
    DemoPost(
        "79000001002",
        "Эксклюзив: полный курс иллюстрации",
        "Шесть часов материала: от скетча до финального арта. Доступно по подписке платформы Creavity.",
        True,
        "creative",
        2,
        video_url="https://youtu.be/aircAruvnKk",
    ),
    DemoPost(
        "79000001003",
        "Путешествие на Байкал",
        "Фотоотчёт, маршрут на три дня и советы, как не переохладиться у воды в межсезонье.",
        False,
        "lifestyle",
        6,
        video_url=DEMO_RUTUBE,
    ),
    DemoPost(
        "79000001003",
        "Как собрать бюджетный поход",
        "Чек-лист снаряжения до 15 кг, список продуктов и типичные ошибки новичков в палаточном кемпинге.",
        False,
        "lifestyle",
        7,
    ),
    DemoPost(
        "79000001004",
        "ЗОЖ-рецепты: смузи на каждый день",
        "Три базовых рецепта на неделю: зелёный, ягодный и белковый. Без дорогих суперфудов.",
        False,
        "lifestyle",
        3,
    ),
    DemoPost(
        "79000001004",
        "Тренировка для спины: закрытый урок",
        "Комплекс на 25 минут с акцентом на осанку. Видео и PDF-план — только для подписчиков платформы.",
        True,
        "lifestyle",
        1,
        video_url=DEMO_VK,
    ),
    DemoPost(
        "79000001001",
        "Заметки разработчика",
        "Почему я люблю utility-first CSS: меньше контекстных переключений и быстрее прототипирование интерфейсов.",
        False,
        "tech",
        8,
        video_url=DEMO_DZEN,
    ),
    DemoPost(
        "79000001001",
        "Продвинутый React: паттерны",
        "Compound components, render props и когда не стоит выносить всё в хуки. Эксклюзив для подписчиков.",
        True,
        "tech",
        2,
    ),
    DemoPost(
        "79000001005",
        "Side-project без выгорания",
        "Как совмещать основную работу и свой продукт: границы времени, MVP и честные ожидания от аудитории.",
        False,
        "business",
        4,
    ),
    DemoPost(
        "79000001005",
        "Финмодель для SaaS: шаблон и разбор",
        "Unit-экономика, CAC/LTV и сценарии роста на 12 месяцев. Таблица и комментарии — по подписке.",
        True,
        "business",
        1,
    ),
    DemoPost(
        "79000001006",
        "5 методов запоминания для студентов",
        "Интервалы, активное recall и карты памяти — короткий гайд с примерами под экзамены.",
        False,
        "education",
        5,
    ),
    DemoPost(
        "79000001006",
        "Подготовка к собеседованию: 20 вопросов",
        "Разбор типовых вопросов HR и техлида с формулировками ответов. Полный список — для подписчиков.",
        True,
        "education",
        3,
    ),
    DemoPost(
        "79000001001",
        "Docker для авторов контента",
        "Как поднять локальную среду Creavity за пять минут: compose, env и проверка health-endpoint.",
        False,
        "tech",
        0,
    ),
)


class Command(BaseCommand):
    """Создаёт демо-авторов и публикации по мотивам HTML-шаблона Creavity."""

    help = "Загружает демо-авторов и публикации (бесплатные и платные) для проверки ленты и каталога."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Регистрирует флаг принудительного пересоздания демо-данных."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Удалить демо-публикации и пересоздать их заново.",
        )

    def handle(self, *args: object, **options: object) -> None:
        """Создаёт или обновляет демо-данные в базе."""
        force = bool(options.get("force"))
        demo_phones = [author.phone for author in DEMO_AUTHORS]

        with transaction.atomic():
            if force:
                deleted_posts, _ = Post.objects.filter(author__phone__in=demo_phones).delete()
                self.stdout.write(f"Удалено публикаций: {deleted_posts}")

            authors_by_phone: dict[str, User] = {}
            for demo_author in DEMO_AUTHORS:
                user, created = User.objects.get_or_create(
                    phone=demo_author.phone,
                    defaults={"display_name": demo_author.display_name},
                )
                if user.display_name != demo_author.display_name:
                    user.display_name = demo_author.display_name
                    user.save(update_fields=["display_name"])
                if created:
                    user.set_password(DEMO_PASSWORD)
                    user.save(update_fields=["password"])
                authors_by_phone[demo_author.phone] = user

            created_count = 0
            skipped_count = 0
            now = timezone.now()

            for demo_post in DEMO_POSTS:
                author = authors_by_phone[demo_post.author_phone]
                exists = Post.objects.filter(author=author, title=demo_post.title).exists()
                if exists and not force:
                    skipped_count += 1
                    continue

                Post.objects.update_or_create(
                    author=author,
                    title=demo_post.title,
                    defaults={
                        "body": demo_post.body,
                        "is_paid": demo_post.is_paid,
                        "topic": demo_post.topic,
                        "video_url": demo_post.video_url,
                        "created_at": now - timezone.timedelta(days=demo_post.days_ago),
                    },
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Демо-данные готовы: авторов {len(DEMO_AUTHORS)}, "
                f"обработано публикаций {created_count}, пропущено {skipped_count}.",
            ),
        )
        self.stdout.write(f"Пароль демо-авторов: {DEMO_PASSWORD}")
        self.stdout.write("Пример входа: телефон 79000001001, пароль DemoPass123")
