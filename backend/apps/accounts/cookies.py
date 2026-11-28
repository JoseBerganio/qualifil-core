"""Helpers for the httpOnly JWT cookie transport used by web clients."""

from django.conf import settings


def _cookie_kwargs():
    return {
        "path": settings.AUTH_COOKIE_PATH,
        "domain": settings.AUTH_COOKIE_DOMAIN,
        "secure": settings.AUTH_COOKIE_SECURE,
        "samesite": settings.AUTH_COOKIE_SAMESITE,
    }


def set_auth_cookies(response, *, access_token, refresh_token):
    """Write the access and refresh tokens as httpOnly cookies."""

    response.set_cookie(
        settings.AUTH_COOKIE_ACCESS_NAME,
        access_token,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        **_cookie_kwargs(),
    )
    if refresh_token:
        response.set_cookie(
            settings.AUTH_COOKIE_REFRESH_NAME,
            refresh_token,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            httponly=True,
            **_cookie_kwargs(),
        )
    return response


def clear_auth_cookies(response):
    """Remove both authentication cookies from the client."""

    for name in (
        settings.AUTH_COOKIE_ACCESS_NAME,
        settings.AUTH_COOKIE_REFRESH_NAME,
    ):
        response.delete_cookie(
            name,
            path=settings.AUTH_COOKIE_PATH,
            domain=settings.AUTH_COOKIE_DOMAIN,
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )
    return response
