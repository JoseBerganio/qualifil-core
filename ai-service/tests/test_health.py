"""Health endpoint tests for the AI service (Sprint 01C)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_liveness_returns_expected_payload(client: TestClient):
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "service": "ai-service",
        "environment": "testing",
        "version": "0.1.0",
    }


def test_readiness_reports_service_checks(client: TestClient):
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert set(data["checks"]) == {"service", "configuration", "providers"}
    assert all(data["checks"].values())


def test_requests_receive_a_request_id_header(client: TestClient):
    response = client.get("/health/live")

    assert response.headers["X-Request-ID"]


def test_supplied_request_id_is_echoed(client: TestClient):
    response = client.get(
        "/health/live", headers={"X-Request-ID": "test-request-id"}
    )

    assert response.headers["X-Request-ID"] == "test-request-id"


def test_health_endpoints_do_not_require_internal_authentication(client: TestClient):
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200
