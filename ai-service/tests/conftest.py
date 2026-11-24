"""Shared pytest fixtures for the AI service tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

TEST_ENV = {
    "APP_ENV": "testing",
    "APP_VERSION": "0.1.0",
    "AI_SERVICE_API_KEY": "test-internal-key",
    "EMBEDDING_MODEL": "test/embedding-model",
    "RERANKER_MODEL": "test/reranker-model",
    "LLM_MODEL": "test/llm-model",
}


@pytest.fixture
def settings() -> Settings:
    return Settings.from_env(TEST_ENV)


@pytest.fixture
def app(settings: Settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(settings: Settings) -> dict[str, str]:
    return {"X-Internal-API-Key": settings.internal_api_key}
