"""
QUALIFIL backend settings — base configuration.

Environment variables are read from the root .env file (see .env.example).
development.py and testing.py adjust the shared base for their environments.
"""

import os
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

APP_NAME = os.environ.get("APP_NAME", "QUALIFIL")
APP_ENV = os.environ.get("APP_ENV", "development")
APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")


def _get_env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and not value:
        raise ImproperlyConfigured(f"The environment variable {name} is required.")
    return value


def _get_bool(name, default=False):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


DEBUG = _get_bool("APP_DEBUG", False)

SECRET_KEY = _get_env("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # Development-only fallback; do not use outside local development.
        SECRET_KEY = "django-insecure-development-only-key"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set when APP_DEBUG is false."
        )

ALLOWED_HOSTS = [
    host.strip()
    for host in _get_env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "api",
    "apps.accounts",
    "apps.audit",
    "apps.applications",
    "apps.distributions",
    "apps.documents",
    "apps.eligibility",
    "apps.notifications",
    "apps.organizations",
    "apps.programs",
    "apps.residents",
    "apps.reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "api.logging.RequestIDMiddleware",
    "api.logging.RequestLogMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Internationalization and general settings
# ---------------------------------------------------------------------------

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-us")
TIME_ZONE = os.environ.get("APP_TIME_ZONE", "Asia/Manila")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ---------------------------------------------------------------------------
# Database (PostgreSQL 18 + pgvector)
# ---------------------------------------------------------------------------

PGVECTOR_EXTENSION = "vector"


def _parse_database_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured("DATABASE_URL must use the postgresql:// scheme.")
    if not parsed.hostname:
        raise ImproperlyConfigured("DATABASE_URL must include a hostname.")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/") or _get_env("POSTGRES_DB", "qualifil"),
        "USER": parsed.username or _get_env("POSTGRES_USER", "qualifil"),
        "PASSWORD": parsed.password or _get_env("POSTGRES_PASSWORD", ""),
        "HOST": parsed.hostname,
        "PORT": parsed.port or _get_env("POSTGRES_PORT", 5432),
    }


DATABASES = {
    "default": _parse_database_url(
        _get_env(
            "DATABASE_URL",
            "postgresql://qualifil@localhost:5432/qualifil",
        )
    )
}

# ---------------------------------------------------------------------------
# Cache and background processing (Redis)
# ---------------------------------------------------------------------------

REDIS_URL = _get_env("REDIS_URL", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

CELERY_BROKER_URL = _get_env("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = _get_env("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = _get_bool("CELERY_TASK_ALWAYS_EAGER", False)
CELERY_TASK_EAGER_PROPAGATES = _get_bool("CELERY_TASK_EAGER_PROPAGATES", True)

# ---------------------------------------------------------------------------
# Object storage (S3-compatible, e.g. MinIO in development)
# ---------------------------------------------------------------------------

AWS_ACCESS_KEY_ID = _get_env("S3_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = _get_env("S3_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = _get_env("S3_BUCKET_NAME", "qualifil-documents")
AWS_S3_ENDPOINT_URL = _get_env("S3_ENDPOINT_URL") or (
    "http://localhost:9000" if DEBUG else ""
)
AWS_S3_REGION_NAME = _get_env("S3_REGION", "ap-southeast-1")

STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

# ---------------------------------------------------------------------------
# Django REST framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.environ.get("DEFAULT_PAGE_SIZE", 50)),
    "EXCEPTION_HANDLER": "api.errors.exception_handler",
}

# ---------------------------------------------------------------------------
# Structured request logging
# ---------------------------------------------------------------------------

LOG_LEVEL = _get_env("LOG_LEVEL", "INFO").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "api.logging.JSONFormatter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
