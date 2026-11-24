"""FastAPI application for the QUALIFIL AI service."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware import RequestContextMiddleware
from app.api.routes import health, models
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.services.model_registry import ModelRegistry

DESCRIPTION = (
    "Internal AI service for QUALIFIL. It produces derived outputs only and "
    "must never make authoritative eligibility or approval decisions. "
    "The service is called by the Django backend, not by web or mobile "
    "clients."
)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the AI service application."""
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    is_production = settings.is_production
    app = FastAPI(
        title="QUALIFIL AI Service",
        description=DESCRIPTION,
        version=settings.app_version,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
    )

    app.state.settings = settings
    app.state.model_registry = ModelRegistry.from_settings(settings)

    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(models.router)

    return app


app = create_app()
