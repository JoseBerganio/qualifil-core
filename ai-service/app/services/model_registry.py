"""Registry of models configured for the AI service.

The registry records configuration and lifecycle state only. It does not load
models; loading and inference arrive with Sprint 03D.
"""

from __future__ import annotations

from app.core.config import Settings
from app.schemas.models import ModelRole, ModelState, ModelStatus


class ModelRegistry:
    """Tracks the configured embedding, reranker, and explanation models."""

    def __init__(self, statuses: list[ModelStatus]) -> None:
        self._statuses = list(statuses)

    @classmethod
    def from_settings(cls, settings: Settings) -> "ModelRegistry":
        return cls(
            [
                ModelStatus(
                    role=ModelRole.EMBEDDING,
                    name=settings.embedding_model,
                    device=settings.embedding_device,
                    status=ModelState.NOT_LOADED,
                ),
                ModelStatus(
                    role=ModelRole.RERANKER,
                    name=settings.reranker_model,
                    device=settings.reranker_device,
                    status=ModelState.NOT_LOADED,
                ),
                ModelStatus(
                    role=ModelRole.EXPLANATION,
                    name=settings.llm_model,
                    device=None,
                    status=ModelState.NOT_LOADED,
                ),
            ]
        )

    def statuses(self) -> list[ModelStatus]:
        """Return a copy of every configured model status."""
        return list(self._statuses)

    def get(self, role: ModelRole) -> ModelStatus | None:
        """Return the status for a single role, if configured."""
        for status in self._statuses:
            if status.role == role:
                return status
        return None
