"""Standardized API error response tests (Sprint 01B)."""

from rest_framework import status
from rest_framework.test import APIClient

from api.errors import (
    BadRequest,
    Conflict,
    Forbidden,
    NotFound,
    Unauthorized,
    error_payload,
)


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
        "BAD_REQUEST",
        "Invalid request.",
        400,
        details=[{"field": "name", "message": "This field is required."}],
    )
    assert payload["error"]["details"] == [
        {"field": "name", "message": "This field is required."}
    ]


def test_custom_api_errors_use_drf_status_codes():
    assert BadRequest().status_code == 400
    assert Unauthorized().status_code == 401
    assert Forbidden().status_code == 403
    assert NotFound().status_code == 404
    assert Conflict().status_code == 409


def test_unknown_url_returns_standard_not_found():
    response = APIClient().get("/api/v1/no-such-endpoint/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    error = body["error"]
    assert error["code"] == "NOT_FOUND"
    assert error["status"] == 404
    assert error["message"]
