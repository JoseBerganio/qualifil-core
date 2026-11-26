"""Configuration tests for the AI service (Sprint 01C)."""

from __future__ import annotations

import pytest

from app.core.config import (
    DEFAULT_INTERNAL_API_KEY,
    ConfigurationError,
    Settings,
)


def test_defaults_are_available_for_development():
    settings = Settings.from_env({})

    assert settings.app_env == "development"
    assert settings.port == 8001
    assert settings.internal_api_key == DEFAULT_INTERNAL_API_KEY
    assert settings.embedding_model == "Qwen/Qwen3-Embedding-0.6B"
    assert settings.reranker_model == "Qwen/Qwen3-Reranker-0.6B"


def test_environment_values_override_defaults():
    settings = Settings.from_env(
        {
            "APP_NAME": "QUALIFIL Test",
            "APP_ENV": "testing",
            "APP_VERSION": "9.9.9",
            "AI_SERVICE_HOST": "127.0.0.1",
            "AI_SERVICE_PORT": "9001",
            "AI_SERVICE_API_KEY": "secret-key",
            "AI_SERVICE_TIMEOUT_SECONDS": "15",
            "LOG_LEVEL": "debug",
            "EMBEDDING_MODEL": "custom/embedding",
            "EMBEDDING_DEVICE": "cuda",
            "RERANKER_MODEL": "custom/reranker",
            "RERANKER_DEVICE": "cuda",
            "LLM_PROVIDER": "test-provider",
            "LLM_MODEL": "test-llm",
        }
    )

    assert settings.app_name == "QUALIFIL Test"
    assert settings.app_env == "testing"
    assert settings.app_version == "9.9.9"
    assert settings.host == "127.0.0.1"
    assert settings.port == 9001
    assert settings.internal_api_key == "secret-key"
    assert settings.request_timeout_seconds == 15
    assert settings.log_level == "DEBUG"
    assert settings.embedding_model == "custom/embedding"
    assert settings.embedding_device == "cuda"
    assert settings.reranker_model == "custom/reranker"
    assert settings.reranker_device == "cuda"
    assert settings.llm_provider == "test-provider"
    assert settings.llm_model == "test-llm"


def test_missing_api_key_is_rejected_outside_development():
    with pytest.raises(ConfigurationError):
        Settings.from_env({"APP_ENV": "production"})


def test_production_requires_explicit_debug_and_production_flag():
    settings = Settings.from_env(
        {"APP_ENV": "production", "AI_SERVICE_API_KEY": "production-key"}
    )

    assert settings.is_production is True
    assert settings.debug is False


def test_invalid_port_is_rejected():
    with pytest.raises(ConfigurationError):
        Settings.from_env({"AI_SERVICE_PORT": "not-a-number"})

    with pytest.raises(ConfigurationError):
        Settings.from_env({"AI_SERVICE_PORT": "70000"})


def test_invalid_timeout_is_rejected():
    with pytest.raises(ConfigurationError):
        Settings.from_env({"AI_SERVICE_TIMEOUT_SECONDS": "0"})
