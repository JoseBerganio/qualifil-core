"""Model-status schemas."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from app.schemas.common import ServiceResponse


class ModelRole(str, Enum):
    """The purpose a configured model serves in the AI service."""

    EMBEDDING = "embedding"
    RERANKER = "reranker"
    EXPLANATION = "explanation"


class ModelState(str, Enum):
    """Lifecycle state of a configured model."""

    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    UNAVAILABLE = "unavailable"


class ModelStatus(ServiceResponse):
    """Reported status for one configured model."""

    role: ModelRole
    name: str
    device: str | None = None
    revision: str | None = None
    status: ModelState = ModelState.NOT_LOADED


class ModelStatusResponse(ServiceResponse):
    """Status of every model configured for the AI service."""

    status: Literal["ok"] = "ok"
    models: list[ModelStatus]
