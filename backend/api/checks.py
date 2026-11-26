"""System checks for the QUALIFIL backend (Sprint 01B)."""

from django.core.checks import Error, Tags, Warning, register


@register(Tags.database)
def pgvector_extension_check(app_configs=None, **kwargs):
    """Verify the pgvector extension is enabled on the default database.

    A missing extension is a configuration error. An unreachable database is
    reported as a warning so that commands such as ``manage.py check`` remain
    usable before local infrastructure has been started.
    """
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
            Warning(
                f"Could not verify the pgvector extension: {exc}",
                hint=(
                    "Start the database (or fix DATABASE_URL) and run "
                    "manage.py check again."
                ),
                id="api.W001",
            )
        )
    return errors
