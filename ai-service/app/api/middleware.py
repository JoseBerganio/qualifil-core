"""HTTP middleware for the QUALIFIL AI service."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.errors import error_payload
from app.core.logging import REQUEST_ID_HEADER

logger = logging.getLogger("ai_service.requests")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID, log the request, and standardize 500 responses."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id
        started = time.monotonic()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.monotonic() - started) * 1000, 2)
            logger.exception(
                "Unhandled service error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
            )
            response = JSONResponse(
                status_code=500,
                content=error_payload(
                    "INTERNAL_SERVER_ERROR",
                    "An unexpected error occurred.",
                    500,
                ),
            )

        duration_ms = round((time.monotonic() - started) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id

        if response.status_code < 500:
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
        return response
