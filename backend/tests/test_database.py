"""Database and cache connectivity tests (Sprint 01B)."""

import pytest


def _postgres_available() -> bool:
    """Return whether the configured PostgreSQL database accepts connections."""
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception:
        return False


@pytest.mark.django_db
@pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL is not reachable; start it or set DATABASE_URL.",
)
def test_database_ping():
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1


def test_pgvector_extension_check_runs():
    from api.checks import pgvector_extension_check

    errors = pgvector_extension_check()
    assert isinstance(errors, list)


def test_cache_configured_for_testing():
    from django.core.cache import caches

    caches["default"].set("qualifil_test_key", "value", 30)
    assert caches["default"].get("qualifil_test_key") == "value"
