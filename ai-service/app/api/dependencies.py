"""FastAPI dependencies for the AI service."""

from __future__ import annotations

import hmac

from fastapi import Request

from app.api.errors import ServiceError
from app.core.config import Settings
from app.services.model_registry import ModelRegistry


def get_app_settings(request: Request) -> Settings:
    """Return the settings bound to the running application."""
    return request.app.state.settings


def get_model_registry(request: Request) -> ModelRegistry:
    """Return the model registry bound to the running application."""
    return request.app.state.model_registry


def require_internal_api_key(request: Request) -> None:
    """Require a valid internal service key on private endpoints.

    Health endpoints stay unauthenticated for orchestration probes; every
    model or inference endpoint must be protected with this dependency.
    """
    settings: Settings = request.app.state.settings
    provided = request.headers.get("X-Internal-API-Key", "")

    if not provided:
        raise ServiceError(
            401,
            "UNAUTHENTICATED",
            "Internal service credentials were not provided.",
        )

    if not hmac.compare_digest(
        provided.encode("utf-8"), settings.internal_api_key.encode("utf-8")
    ):
        raise ServiceError(
            403,
            "FORBIDDEN",
            "Invalid internal service credentials.",
        )
