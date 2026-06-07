"""Общие константы проекта — единый источник настраиваемых значений без магических чисел."""

# JWT (переопределение через env в settings)
DEFAULT_JWT_ACCESS_MINUTES = 15
DEFAULT_JWT_REFRESH_DAYS = 1

# Stripe
STRIPE_CURRENCY_MULTIPLIER = 100
DEFAULT_STRIPE_CURRENCY = "rub"
DEFAULT_STRIPE_SUBSCRIPTION_AMOUNT_RUB = 990
DEFAULT_STRIPE_SUCCESS_URL = "http://localhost/payment/success"
DEFAULT_STRIPE_CANCEL_URL = "http://localhost/payment/cancel"
DEFAULT_SITE_URL = "http://localhost"

# Телефон (validators/users)
PHONE_DIGITS_LENGTH = 11
PHONE_COUNTRY_DIGIT = "7"

# Пагинация списка публикаций
DEFAULT_PAGE_SIZE = 10

# Рекомендации: максимум ID в query exclude=
MAX_RECOMMENDED_EXCLUDE_IDS = 50

# Каталог авторов: верхняя граница списка без пагинации
MAX_AUTHORS_LIST = 100

# PostgreSQL
DEFAULT_DB_PORT = "5432"
DEFAULT_DB_USER = "postgres"
DEFAULT_DB_HOST = "localhost"

# Dev-only fallback (production: обязателен SECRET_KEY из env)
DEV_INSECURE_SECRET_KEY = "django-insecure-dev-only-change-me"

# Безопасные возвраты для сервисов (шаблон модулей services/)
DEFAULT_RETURN_VALUE: list[object] = []
DEFAULT_RETURN_DICT: dict[str, object] = {}
