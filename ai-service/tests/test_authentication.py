"""Internal authentication tests for the AI service (Sprint 01C)."""

from __future__ import annotations

from fastapi.testclient import TestClient

MODELS_STATUS_URL = "/internal/v1/models/status"


def test_missing_internal_key_is_rejected(client: TestClient):
    response = client.get(MODELS_STATUS_URL)

    assert response.status_code == 401
    error = response.json()["error"]
    assert error["code"] == "UNAUTHENTICATED"
    assert error["status"] == 401
    assert error["message"]


def test_invalid_internal_key_is_rejected(client: TestClient):
    response = client.get(
        MODELS_STATUS_URL, headers={"X-Internal-API-Key": "wrong-key"}
    )

    assert response.status_code == 403
    error = response.json()["error"]
    assert error["code"] == "FORBIDDEN"
    assert error["status"] == 403


def test_valid_internal_key_is_accepted(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.get(MODELS_STATUS_URL, headers=auth_headers)

    assert response.status_code == 200


def test_internal_key_comparison_is_exact(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.get(
        MODELS_STATUS_URL,
        headers={"X-Internal-API-Key": auth_headers["X-Internal-API-Key"] + " "},
    )

    assert response.status_code == 403
