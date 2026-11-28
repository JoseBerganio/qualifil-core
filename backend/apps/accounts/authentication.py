"""Authentication classes for the two supported client transports."""

from django.conf import settings
from django.http import HttpResponse
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def enforce_csrf(request):
    """Validate the CSRF double-submit token for cookie-authenticated requests.

    DRF API views are wrapped in ``csrf_exempt``, so cookie-based JWT requests
    must explicitly run Django's CSRF middleware checks. Bearer-token requests
    from mobile clients are not vulnerable to CSRF and do not need this.
    """

    middleware = CsrfViewMiddleware(lambda req: HttpResponse())
    response = middleware.process_view(request, lambda req: HttpResponse(), (), {})
    if response is not None:
        raise exceptions.PermissionDenied(
            "CSRF verification failed. Request aborted."
        )


class CookieJWTAuthentication(JWTAuthentication):
    """Read the access token from an httpOnly cookie for web clients.

    When the token arrives through a cookie, unsafe requests must also present
    a matching CSRF token header. Header-authenticated requests continue to use
    the standard ``JWTAuthentication`` class.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS_NAME)
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        if request.method not in SAFE_METHODS:
            enforce_csrf(request)

        return user, validated_token
