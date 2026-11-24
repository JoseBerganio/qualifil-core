"""Django-level error handlers that use the standardized API envelope."""

from django.http import JsonResponse

from api.errors import error_payload


def not_found(request, exception=None):
    return JsonResponse(
        error_payload("NOT_FOUND", "The requested resource was not found.", 404),
        status=404,
    )


def server_error(request, exception=None):
    return JsonResponse(
        error_payload("INTERNAL_SERVER_ERROR", "Internal server error.", 500),
        status=500,
    )
