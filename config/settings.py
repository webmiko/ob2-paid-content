"""Настройки Django для платформы платного контента."""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

from config.constants import (
    DEFAULT_DB_HOST,
    DEFAULT_DB_PORT,
    DEFAULT_DB_USER,
    DEFAULT_JWT_ACCESS_MINUTES,
    DEFAULT_JWT_REFRESH_DAYS,
    DEFAULT_PAGE_SIZE,
    DEFAULT_SITE_URL,
    DEFAULT_SMS_CODE_TTL_SECONDS,
    DEFAULT_SMS_VERIFIED_TTL_SECONDS,
    DEFAULT_STRIPE_CANCEL_URL,
    DEFAULT_STRIPE_CURRENCY,
    DEFAULT_STRIPE_SUBSCRIPTION_AMOUNT_RUB,
    DEFAULT_STRIPE_SUCCESS_URL,
    DEV_INSECURE_SECRET_KEY,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", DEV_INSECURE_SECRET_KEY)
DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "users",
    "posts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

_db_name = os.getenv("DB_NAME")
if _db_name:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db_name,
            "USER": os.getenv("DB_USER", DEFAULT_DB_USER),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", DEFAULT_DB_HOST),
            "PORT": os.getenv("DB_PORT", DEFAULT_DB_PORT),
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

_cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _cors_origins.split(",") if origin.strip()]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": DEFAULT_PAGE_SIZE,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "120/min",
        "auth": "10/min",
        "payment": "30/min",
        "comment_create": "30/hour",
        "comment_delete": "60/hour",
        "account_delete": "5/hour",
        "webhook": "120/min",
        "view_record": "120/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(
            os.getenv("JWT_ACCESS_MINUTES", str(DEFAULT_JWT_ACCESS_MINUTES)),
        ),
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_DAYS", str(DEFAULT_JWT_REFRESH_DAYS))),
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_CURRENCY = os.getenv("STRIPE_CURRENCY", DEFAULT_STRIPE_CURRENCY)
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", DEFAULT_STRIPE_SUCCESS_URL)
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", DEFAULT_STRIPE_CANCEL_URL)
STRIPE_SUBSCRIPTION_AMOUNT = int(
    os.getenv("STRIPE_SUBSCRIPTION_AMOUNT", str(DEFAULT_STRIPE_SUBSCRIPTION_AMOUNT_RUB)),
)
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

SITE_URL = os.getenv("SITE_URL", DEFAULT_SITE_URL).rstrip("/")

USE_HTTPS = os.getenv("USE_HTTPS", "false").lower() in ("1", "true", "yes")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ob2-default-cache",
    },
}

SMS_VERIFICATION_REQUIRED = os.getenv("SMS_VERIFICATION_REQUIRED", "true").lower() in (
    "1",
    "true",
    "yes",
)
SMS_CODE_TTL_SECONDS = int(
    os.getenv("SMS_CODE_TTL_SECONDS", str(DEFAULT_SMS_CODE_TTL_SECONDS)),
)
SMS_VERIFIED_TTL_SECONDS = int(
    os.getenv("SMS_VERIFIED_TTL_SECONDS", str(DEFAULT_SMS_VERIFIED_TTL_SECONDS)),
)
SMS_SHOW_CODE_IN_RESPONSE = os.getenv(
    "SMS_SHOW_CODE_IN_RESPONSE",
    "true" if DEBUG else "false",
).lower() in ("1", "true", "yes")

MIN_SECRET_KEY_LENGTH = 50

if not DEBUG and SECRET_KEY == DEV_INSECURE_SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY must be set when DEBUG is False.")

if not DEBUG and len(SECRET_KEY) < MIN_SECRET_KEY_LENGTH:
    raise ImproperlyConfigured(
        f"SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters when DEBUG is False.",
    )

if USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
