"""Health and readiness schemas."""

from __future__ import annotations

from typing import Literal

from app.schemas.common import ServiceResponse


class LivenessResponse(ServiceResponse):
    """Result of the lightweight liveness check."""

    status: Literal["ok"]
    service: str
    environment: str
    version: str


class ReadinessResponse(ServiceResponse):
    """Result of the readiness check for AI service dependencies."""

    status: Literal["ok", "degraded"]
    checks: dict[str, bool]
