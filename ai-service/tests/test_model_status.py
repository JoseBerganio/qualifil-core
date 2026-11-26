"""Model-status endpoint tests for the AI service (Sprint 01C)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_model_status_lists_configured_models(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.get("/internal/v1/models/status", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    models = {model["role"]: model for model in data["models"]}
    assert set(models) == {"embedding", "reranker", "explanation"}

    assert models["embedding"]["name"] == "test/embedding-model"
    assert models["reranker"]["name"] == "test/reranker-model"
    assert models["explanation"]["name"] == "test/llm-model"


def test_models_report_not_loaded_before_sprint_03d(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.get("/internal/v1/models/status", headers=auth_headers)

    for model in response.json()["models"]:
        assert model["status"] == "not_loaded"


def test_embedding_and_reranker_report_their_devices(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.get("/internal/v1/models/status", headers=auth_headers)
    models = {model["role"]: model for model in response.json()["models"]}

    assert models["embedding"]["device"] == "cpu"
    assert models["reranker"]["device"] == "cpu"
    assert models["explanation"]["device"] is None
