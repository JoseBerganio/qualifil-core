"""Database and cache connectivity tests (Sprint 01B)."""

import pytest


@pytest.mark.django_db
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
