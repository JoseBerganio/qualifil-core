"""Django settings for automated tests (Sprint 01B)."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key-for-automated-tests")

from .base import *  # noqa: E402,F401,F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Optional local fallback for machines without a reachable PostgreSQL test
# database. CI always runs against PostgreSQL; use this only for local checks:
#   $env:DJANGO_TEST_DATABASE = "sqlite"; python -m pytest
if os.environ.get("DJANGO_TEST_DATABASE", "").strip().lower() == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.environ.get("DJANGO_TEST_SQLITE_NAME", ":memory:"),
        }
    }
