"""System checks for the QUALIFIL backend (Sprint 01B)."""

from django.core.checks import Error, Tags, register


@register(Tags.database)
def pgvector_extension_check(app_configs=None, **kwargs):
    """Verify the pgvector extension is enabled on the default database."""
    from django.db import connection

    errors = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT extname FROM pg_extension WHERE extname = 'vector'"
            )
            if cursor.fetchone() is None:
                errors.append(
                    Error(
                        "The pgvector extension is not enabled in the default database.",
                        hint="Run CREATE EXTENSION vector; (see backend/docker/init.sql).",
                        id="api.E001",
                    )
                )
    except Exception as exc:
        errors.append(
            Error(
                f"Could not verify the pgvector extension: {exc}",
                id="api.E002",
            )
        )
    return errors
