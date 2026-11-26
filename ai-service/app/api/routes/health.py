"""Health and readiness endpoints (Sprint 01C)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_app_settings, get_model_registry
from app.core.config import Settings
from app.schemas.health import LivenessResponse, ReadinessResponse
from app.services.model_registry import ModelRegistry

router = APIRouter(tags=["health"])


@router.get(
    "/health/live",
    response_model=LivenessResponse,
    summary="Liveness check",
)
async def liveness(
    settings: Settings = Depends(get_app_settings),
) -> LivenessResponse:
    """Report that the process is running. Requires no external services."""
    return LivenessResponse(
        status="ok",
        service=settings.service_name,
        environment=settings.app_env,
        version=settings.app_version,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",
)
async def readiness(
    response: Response,
    settings: Settings = Depends(get_app_settings),
    registry: ModelRegistry = Depends(get_model_registry),
) -> ReadinessResponse:
    """Report whether the service is ready to accept internal requests.

    Models are expected to be unloaded during the foundation release, so model
    readiness is not required. The check verifies configuration and registry
    availability instead.
    """
    checks = {
        "service": True,
        "configuration": bool(settings.internal_api_key),
        "providers": bool(registry.statuses()),
    }
    healthy = all(checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status="ok" if healthy else "degraded",
        checks=checks,
    )
