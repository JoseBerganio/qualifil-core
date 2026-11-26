"""Environment-based configuration for the QUALIFIL AI service.

Configuration is read from environment variables documented in the root
``.env.example``. The Django backend and the AI service share the same
environment file during local development.

Actual model loading and inference are deferred to v0.3.0. This module only
records which models are configured so the service can report its status.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from dotenv import load_dotenv

# Load the shared repository .env file. Real environment variables take
# precedence so container and CI configuration is never overwritten.
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ENV_FILE, override=False)

DEFAULT_INTERNAL_API_KEY = "development-only-internal-key"

DEVELOPMENT_ENVIRONMENTS = frozenset({"development", "local", "test", "testing"})


class ConfigurationError(RuntimeError):
    """Raised when required AI service configuration is missing or invalid."""


def _get_str(env: Mapping[str, str], name: str, default: str) -> str:
    value = env.get(name, default)
    return value.strip() if isinstance(value, str) else default


def _get_bool(env: Mapping[str, str], name: str, default: bool) -> bool:
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _get_int(
    env: Mapping[str, str],
    name: str,
    default: int,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    raw = env.get(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        value = int(str(raw).strip())
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer.") from exc
    if minimum is not None and value < minimum:
        raise ConfigurationError(f"{name} must be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise ConfigurationError(f"{name} must be at most {maximum}.")
    return value


@dataclass(frozen=True)
class Settings:
    """AI service configuration for a single runtime environment."""

    app_name: str = "QUALIFIL"
    service_name: str = "ai-service"
    app_env: str = "development"
    app_version: str = "0.1.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"
    request_timeout_seconds: int = 60

    internal_api_key: str = DEFAULT_INTERNAL_API_KEY

    embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"
    embedding_device: str = "cpu"
    reranker_model: str = "Qwen/Qwen3-Reranker-0.6B"
    reranker_device: str = "cpu"
    llm_provider: str = "anthropic"
    llm_model: str = "claude-haiku-5-5"

    @property
    def is_production(self) -> bool:
        return self.app_env not in DEVELOPMENT_ENVIRONMENTS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        """Build settings from a mapping, defaulting to the process environment."""
        source = os.environ if env is None else env

        app_env = _get_str(source, "APP_ENV", "development").lower()
        internal_api_key = _get_str(source, "AI_SERVICE_API_KEY", "")
        if not internal_api_key:
            if app_env in DEVELOPMENT_ENVIRONMENTS:
                # Development-only fallback; deployments must supply a key.
                internal_api_key = DEFAULT_INTERNAL_API_KEY
            else:
                raise ConfigurationError(
                    "AI_SERVICE_API_KEY must be set outside development."
                )

        return cls(
            app_name=_get_str(source, "APP_NAME", "QUALIFIL"),
            app_env=app_env,
            app_version=_get_str(source, "APP_VERSION", "0.1.0"),
            debug=_get_bool(source, "APP_DEBUG", False),
            host=_get_str(source, "AI_SERVICE_HOST", "0.0.0.0"),
            port=_get_int(source, "AI_SERVICE_PORT", 8001, 1, 65535),
            log_level=_get_str(source, "LOG_LEVEL", "INFO").upper(),
            request_timeout_seconds=_get_int(
                source, "AI_SERVICE_TIMEOUT_SECONDS", 60, 1
            ),
            internal_api_key=internal_api_key,
            embedding_model=_get_str(
                source, "EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B"
            ),
            embedding_device=_get_str(source, "EMBEDDING_DEVICE", "cpu"),
            reranker_model=_get_str(
                source, "RERANKER_MODEL", "Qwen/Qwen3-Reranker-0.6B"
            ),
            reranker_device=_get_str(source, "RERANKER_DEVICE", "cpu"),
            llm_provider=_get_str(source, "LLM_PROVIDER", "anthropic"),
            llm_model=_get_str(source, "LLM_MODEL", "claude-haiku-5-5"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings.from_env()
