"""Health endpoint tests (Sprint 01B)."""

from rest_framework.test import APIClient

LIVENESS_URL = "/api/v1/health/"


def test_liveness_returns_200_with_expected_payload():
    response = APIClient().get(LIVENESS_URL)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "version" in data


def test_requests_include_a_request_id_header():
    response = APIClient().get(LIVENESS_URL)
    assert response.status_code == 200
    assert response["X-Request-ID"]


def test_readiness_returns_service_states():
    response = APIClient().get("/api/v1/health/ready/")
    assert response.status_code in (200, 503)
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert set(data["checks"]) == {"database", "redis", "celery"}
