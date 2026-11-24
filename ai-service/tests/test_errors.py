"""Standardized error response tests for the AI service (Sprint 01C)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import Field

from app.api.errors import error_payload
from app.main import create_app
from app.schemas.common import ServiceRequest


def test_error_payload_shape():
    payload = error_payload("NOT_FOUND", "Not found.", 404)

    assert payload == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Not found.",
            "status": 404,
        }
    }


def test_error_payload_includes_details_when_present():
    payload = error_payload(
        "UNPROCESSABLE_ENTITY",
        "Request validation failed.",
        422,
        details=[{"field": "name", "message": "Field required."}],
    )

    assert payload["error"]["details"] == [
        {"field": "name", "message": "Field required."}
    ]


def test_unknown_route_returns_standard_not_found(client: TestClient):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert error["status"] == 404
    assert error["message"]


def test_wrong_method_returns_standard_error(client: TestClient):
    response = client.post("/health/live")

    assert response.status_code == 405
    error = response.json()["error"]
    assert error["code"] == "METHOD_NOT_ALLOWED"
    assert error["status"] == 405


class EchoRequest(ServiceRequest):
    name: str = Field(min_length=1)


@pytest.fixture
def validation_app(settings):
    app = create_app(settings)

    @app.post("/test/echo")
    async def echo(payload: EchoRequest):
        return {"name": payload.name}

    return app


def test_validation_errors_use_standard_envelope(validation_app):
    with TestClient(validation_app) as client:
        response = client.post("/test/echo", json={"unexpected": "value"})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UNPROCESSABLE_ENTITY"
    assert error["status"] == 422
    assert error["details"]
    assert any(detail["field"] == "name" for detail in error["details"])


def test_extra_fields_are_rejected(validation_app):
    with TestClient(validation_app) as client:
        response = client.post(
            "/test/echo", json={"name": "Resident", "unexpected": "value"}
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNPROCESSABLE_ENTITY"


def test_unhandled_errors_use_standard_envelope(settings):
    app = create_app(settings)

    @app.get("/test/boom")
    async def boom():
        raise RuntimeError("boom")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test/boom")

    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "INTERNAL_SERVER_ERROR"
    assert error["status"] == 500
    assert response.headers["X-Request-ID"]
