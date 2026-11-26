"""Standardized API error responses for the QUALIFIL backend."""

import logging

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

STATUS_CODE_TO_ERROR_CODE = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHENTICATED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_409_CONFLICT: "CONFLICT",
    status.HTTP_410_GONE: "GONE",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "UNSUPPORTED_MEDIA_TYPE",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "UNPROCESSABLE_ENTITY",
    status.HTTP_429_TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
    status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
}


class APIError(APIException):
    """Base class for QUALIFIL API errors with the standardized shape."""

    default_detail = "An error occurred."
    default_code = "ERROR"
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        super().__init__(detail=detail, code=code or self.default_code)


class BadRequest(APIError):
    """Request is malformed or invalid."""

    default_detail = "Invalid request."
    default_code = "BAD_REQUEST"
    default_status_code = status.HTTP_400_BAD_REQUEST


class Unauthorized(APIError):
    """Authentication credentials were not provided."""

    default_detail = "Authentication credentials were not provided."
    default_code = "UNAUTHENTICATED"
    default_status_code = status.HTTP_401_UNAUTHORIZED


class Forbidden(APIError):
    """Authenticated user lacks permission for this action."""

    default_detail = "You do not have permission to perform this action."
    default_code = "FORBIDDEN"
    default_status_code = status.HTTP_403_FORBIDDEN


class NotFound(APIError):
    """The requested resource was not found."""

    default_detail = "The requested resource was not found."
    default_code = "NOT_FOUND"
    default_status_code = status.HTTP_404_NOT_FOUND


class Conflict(APIError):
    """The request conflicts with the current state of the resource."""

    default_detail = "The request conflicts with the current state of the resource."
    default_code = "CONFLICT"
    default_status_code = status.HTTP_409_CONFLICT


def _error_code_for_status(status_code):
    return STATUS_CODE_TO_ERROR_CODE.get(status_code, "ERROR")


def _extract_details(data):
    """Convert DRF error data into a list of {"field", "message"} entries."""
    details = []
    if isinstance(data, dict):
        for field, value in data.items():
            if isinstance(value, (list, tuple)):
                for message in value:
                    details.append({"field": field, "message": str(message)})
            elif value is not None:
                details.append({"field": field, "message": str(value)})
    elif isinstance(data, (list, tuple)):
        for item in data:
            details.append({"message": str(item)})
    elif data is not None:
        details.append({"message": str(data)})
    return details


def error_payload(code, message, status_code, details=None):
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


def exception_handler(exc, context):
    """Wrap DRF's handler so every response uses the project error shape."""
    response = drf_exception_handler(exc, context)
    if response is None:
        return None
    data = response.data or {}
    details = _extract_details(data)
    message = ""
    if isinstance(data, dict) and data.get("detail") is not None:
        message = str(data["detail"])
    if not message and details:
        message = details[0]["message"]
    response.data = error_payload(
        code=_error_code_for_status(response.status_code),
        message=message or "Request failed.",
        status_code=response.status_code,
        details=details or None,
    )
    return response
