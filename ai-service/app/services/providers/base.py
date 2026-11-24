"""Model provider interfaces for the AI service.

Concrete model loading and inference implementations are introduced in
Sprint 03D. These interfaces keep the service layer independent of a specific
model runtime and allow deterministic test doubles.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from app.schemas.models import ModelRole, ModelState, ModelStatus


class ModelProvider(ABC):
    """Base class for a configured model provider."""

    role: ModelRole

    def __init__(
        self,
        name: str,
        device: str | None = None,
        revision: str | None = None,
    ) -> None:
        self.name = name
        self.device = device
        self.revision = revision
        self._state = ModelState.NOT_LOADED

    @property
    def status(self) -> ModelStatus:
        """Return the current provider status without triggering loading."""
        return ModelStatus(
            role=self.role,
            name=self.name,
            device=self.device,
            revision=self.revision,
            status=self._state,
        )

    @abstractmethod
    async def load(self) -> None:
        """Load the model into memory."""

    @abstractmethod
    async def unload(self) -> None:
        """Release the model's resources."""


class EmbeddingProvider(ModelProvider):
    """Produces vector representations for text."""

    role = ModelRole.EMBEDDING

    @abstractmethod
    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""


class RerankProvider(ModelProvider):
    """Orders candidate documents by relevance to a query."""

    role = ModelRole.RERANKER

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: Sequence[str],
        top_n: int | None = None,
    ) -> list[tuple[int, float]]:
        """Return ``(document_index, score)`` pairs, best first."""


class ExplanationProvider(ModelProvider):
    """Produces natural-language explanations from validated input."""

    role = ModelRole.EXPLANATION

    @abstractmethod
    async def explain(self, payload: dict) -> str:
        """Return an explanation for the supplied, already-validated payload."""
