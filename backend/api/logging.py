"""Structured request logging for the QUALIFIL backend (Sprint 01B)."""

import json
import logging
import uuid
from datetime import datetime, timezone

REQUEST_ID_HEADER = "X-Request-ID"


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured log ingestion."""

    KNOWN_FIELDS = ("request_id", "method", "path", "status_code", "duration_ms")

    def format(self, record):
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in self.KNOWN_FIELDS:
            value = getattr(record, key, None)
            if value is not None:
                data[key] = value
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data, default=str)


class RequestIDMiddleware:
    """Assign an X-Request-ID to every request and echo it on the response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.request_id = request_id
        response = self.get_response(request)
        response[REQUEST_ID_HEADER] = request_id
        return response


class RequestLogMiddleware:
    """Log the method, path, status code and duration of each request."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("api.requests")

    def __call__(self, request):
        import time

        started = time.monotonic()
        try:
            response = self.get_response(request)
        except Exception:
            self.logger.exception(
                "Request failed",
                extra={"request_id": getattr(request, "request_id", None)},
            )
            raise
        duration_ms = round((time.monotonic() - started) * 1000, 2)
        self.logger.info(
            "Request completed",
            extra={
                "request_id": getattr(request, "request_id", None),
                "method": request.method,
                "path": request.get_full_path(),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
