"""Internal model-status endpoints (Sprint 01C)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_model_registry, require_internal_api_key
from app.schemas.models import ModelStatusResponse
from app.services.model_registry import ModelRegistry

router = APIRouter(
    prefix="/internal/v1",
    tags=["internal"],
    dependencies=[Depends(require_internal_api_key)],
)


@router.get(
    "/models/status",
    response_model=ModelStatusResponse,
    summary="Report configured model status",
)
async def model_status(
    registry: ModelRegistry = Depends(get_model_registry),
) -> ModelStatusResponse:
    """Return the configured models and their lifecycle state.

    This endpoint is for the Django backend. It is never exposed to web or
    mobile clients.
    """
    return ModelStatusResponse(status="ok", models=registry.statuses())
