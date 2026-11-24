"""Standardized error responses for the QUALIFIL AI service.

The error envelope intentionally matches the Django backend so internal
clients can use one error-handling code path across both services.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

STATUS_CODE_TO_ERROR_CODE = {
    400: "BAD_REQUEST",
    401: "UNAUTHENTICATED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    410: "GONE",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: "UNPROCESSABLE_ENTITY",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_SERVER_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


class ServiceError(Exception):
    """Base exception for errors that produce the standardized envelope."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[dict] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def error_payload(
    code: str,
    message: str,
    status_code: int,
    details: list[dict] | None = None,
) -> dict:
    """Build the standardized error response body."""
    payload = {
        "error": {
            "code": code,
            "message": message,
            "status": status_code,
        }
    }
    if details:
        payload["error"]["details"] = details
    return payload


def _error_code_for_status(status_code: int) -> str:
    return STATUS_CODE_TO_ERROR_CODE.get(status_code, "ERROR")


def _json_error(
    status_code: int,
    code: str,
    message: str,
    details: list[dict] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error_payload(code, message, status_code, details),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the AI service's exception handlers to an application."""

    @app.exception_handler(ServiceError)
    async def service_error_handler(
        request: Request, exc: ServiceError
    ) -> JSONResponse:
        return _json_error(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = []
        for error in exc.errors():
            location = [
                str(part) for part in error.get("loc", ()) if part != "body"
            ]
            details.append(
                {
                    "field": ".".join(location) or None,
                    "message": str(error.get("msg", "Invalid value.")),
                }
            )
        return _json_error(
            422,
            "UNPROCESSABLE_ENTITY",
            "Request validation failed.",
            details or None,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail = exc.detail
        message = detail if isinstance(detail, str) else "Request failed."
        return _json_error(
            exc.status_code,
            _error_code_for_status(exc.status_code),
            message,
        )
