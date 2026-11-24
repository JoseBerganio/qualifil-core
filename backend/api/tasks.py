"""Celery tasks for the QUALIFIL backend (Sprint 01B)."""

import logging

from config.celery import app

logger = logging.getLogger(__name__)


@app.task(name="api.tasks.probe")
def probe(message="probe"):
    """Simple task used by the backend health and Celery tests."""
    logger.info("Celery probe task executed: %s", message)
    return {"status": "ok", "message": message}
