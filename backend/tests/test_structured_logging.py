"""Structured request logging tests (Sprint 01B)."""

import json
import logging

from api.logging import JSONFormatter, RequestIDMiddleware, RequestLogMiddleware
from rest_framework.test import APIClient

LIVENESS_URL = "/api/v1/health/"


def _make_log_record():
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=None,
        exc_info=None,
    )
    record.request_id = "req-123"
    record.method = "GET"
    record.path = "/api/v1/health/"
    record.status_code = 200
    record.duration_ms = 3.5
    return record


def test_json_formatter_outputs_json_fields():
    formatter = JSONFormatter()
    data = json.loads(formatter.format(_make_log_record()))
    assert data["message"] == "hello"
    assert data["level"] == "INFO"
    assert data["logger"] == "test"
    assert data["request_id"] == "req-123"
    assert data["method"] == "GET"
    assert data["path"] == "/api/v1/health/"
    assert data["status_code"] == 200
    assert data["duration_ms"] == 3.5
    assert "timestamp" in data


def test_request_id_middleware_assigns_header():
    response = APIClient().get(LIVENESS_URL)
    assert response["X-Request-ID"]


def test_request_log_middleware_logs_completed_requests(caplog):
    client = APIClient()
    with caplog.at_level(logging.INFO, logger="api.requests"):
        response = client.get(LIVENESS_URL)
    assert response.status_code == 200
    completed = [r for r in caplog.records if r.getMessage() == "Request completed"]
    assert len(completed) == 1
    record = completed[0]
    assert record.method == "GET"
    assert record.path == LIVENESS_URL
    assert record.status_code == 200
    assert record.duration_ms >= 0
