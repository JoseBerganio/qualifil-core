"""Tests for the AI service application factory and provider interfaces."""

from __future__ import annotations

from app.core.config import Settings
from app.main import create_app
from app.services.providers.base import (
    EmbeddingProvider,
    ExplanationProvider,
    ModelProvider,
    RerankProvider,
)
from app.services.model_registry import ModelRegistry


def test_create_app_binds_settings_and_registry(settings: Settings):
    app = create_app(settings)

    assert app.state.settings is settings
    assert isinstance(app.state.model_registry, ModelRegistry)


def test_docs_are_available_outside_production(settings: Settings):
    app = create_app(settings)

    assert app.docs_url == "/docs"
    assert app.openapi_url == "/openapi.json"


def test_docs_are_disabled_in_production():
    settings = Settings.from_env(
        {"APP_ENV": "production", "AI_SERVICE_API_KEY": "production-key"}
    )
    app = create_app(settings)

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None


def test_provider_interfaces_declare_their_model_roles():
    assert issubclass(EmbeddingProvider, ModelProvider)
    assert issubclass(RerankProvider, ModelProvider)
    assert issubclass(ExplanationProvider, ModelProvider)

    assert EmbeddingProvider.role.value == "embedding"
    assert RerankProvider.role.value == "reranker"
    assert ExplanationProvider.role.value == "explanation"


def test_model_registry_lookup(settings: Settings):
    from app.schemas.models import ModelRole

    registry = ModelRegistry.from_settings(settings)

    assert registry.get(ModelRole.EMBEDDING) is not None
    assert registry.get(ModelRole.RERANKER) is not None
    assert registry.get(ModelRole.EXPLANATION) is not None
