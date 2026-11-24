"""Shared request and response schemas for the AI service."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ServiceRequest(BaseModel):
    """Base class for internal service requests.

    Unknown fields are rejected so contract drift is caught at the boundary.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ServiceResponse(BaseModel):
    """Base class for internal service responses."""

    model_config = ConfigDict(extra="forbid")


class ErrorDetail(BaseModel):
    """A single field-level or general error detail."""

    field: str | None = None
    message: str


class ErrorBody(BaseModel):
    """The error information carried by every failed response."""

    code: str
    message: str
    status: int
    details: list[ErrorDetail] | None = None


class ErrorResponse(ServiceResponse):
    """Standardized error response, matching the Django backend shape."""

    error: ErrorBody
