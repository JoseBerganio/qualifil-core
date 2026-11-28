"""Authentication API views."""

from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import AccessToken

from api.errors import BadRequest, Conflict, Unauthorized

from . import services
from .authentication import enforce_csrf
from .cookies import clear_auth_cookies, set_auth_cookies
from .models import User
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

AUTH_MODE_COOKIE = "cookie"
AUTH_MODE_BEARER = "bearer"


def get_auth_mode(request):
    """Return the explicit client transport, defaulting to bearer tokens."""

    mode = (request.headers.get("X-Auth-Mode") or AUTH_MODE_BEARER).strip().lower()
    return AUTH_MODE_COOKIE if mode == AUTH_MODE_COOKIE else AUTH_MODE_BEARER


def _token_response(request, user, *, access, refresh, status_code=status.HTTP_200_OK):
    payload = {"user": UserSerializer(user).data}
    if get_auth_mode(request) == AUTH_MODE_COOKIE:
        response = Response(payload, status=status_code)
        set_auth_cookies(response, access_token=access, refresh_token=refresh)
        return response

    payload.update({"access": access, "refresh": refresh})
    return Response(payload, status=status_code)


def _raise_for_service_error(exc, *, invalid_message):
    if isinstance(exc, services.AccountLocked):
        raise Throttled(wait=exc.retry_after_seconds)
    if isinstance(exc, services.PasswordValidationFailed):
        raise BadRequest(detail=exc.messages)
    if isinstance(exc, services.InvalidCredentials):
        raise Unauthorized(invalid_message)
    raise exc


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if get_auth_mode(request) == AUTH_MODE_COOKIE:
            enforce_csrf(request)

        try:
            user = services.register_user(**serializer.validated_data)
        except services.EmailAlreadyRegistered:
            raise Conflict("An account with this email address already exists.")
        except services.PasswordValidationFailed as exc:
            raise BadRequest(detail=exc.messages) from exc

        access, refresh = services.issue_tokens_for_user(user)
        return _token_response(
            request,
            user,
            access=access,
            refresh=refresh,
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if get_auth_mode(request) == AUTH_MODE_COOKIE:
            enforce_csrf(request)

        try:
            user = services.authenticate_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                request=request,
            )
        except services.AuthServiceError as exc:
            _raise_for_service_error(
                exc,
                invalid_message="Unable to log in with provided credentials.",
            )

        access, refresh = services.issue_tokens_for_user(user)
        return _token_response(request, user, access=access, refresh=refresh)


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "refresh"

    def post(self, request):
        mode = get_auth_mode(request)
        if mode == AUTH_MODE_COOKIE:
            enforce_csrf(request)
            raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)
        else:
            raw_refresh = (request.data or {}).get("refresh")

        if not raw_refresh:
            raise Unauthorized("A refresh token is required.")

        try:
            access, rotated_refresh = services.rotate_refresh_token(raw_refresh)
        except services.AuthServiceError as exc:
            raise Unauthorized("The refresh token is invalid or expired.") from exc

        user_id = AccessToken(access).payload.get(jwt_settings.USER_ID_CLAIM)
        user = User.objects.filter(pk=user_id, is_active=True).first()
        if user is None:
            raise Unauthorized("The refresh token is invalid or expired.")

        return _token_response(
            request,
            user,
            access=access,
            refresh=rotated_refresh or raw_refresh,
        )


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        mode = get_auth_mode(request)
        if mode == AUTH_MODE_COOKIE:
            enforce_csrf(request)
            raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)
        else:
            raw_refresh = (request.data or {}).get("refresh")

        services.blacklist_refresh_token(raw_refresh)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        if mode == AUTH_MODE_COOKIE:
            clear_auth_cookies(response)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            services.change_password(
                user=request.user,
                current_password=serializer.validated_data["current_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except services.InvalidCredentials as exc:
            raise BadRequest("The current password is incorrect.") from exc
        except services.PasswordValidationFailed as exc:
            raise BadRequest(detail=exc.messages) from exc

        return Response(status=status.HTTP_204_NO_CONTENT)


class CsrfTokenView(APIView):
    """Issue the readable CSRF cookie required by the cookie transport."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        token = get_token(request)
        response = Response({"csrfToken": token})
        response.set_cookie(
            settings.CSRF_COOKIE_NAME,
            token,
            max_age=int(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            ),
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            httponly=False,
            path="/",
        )
        return response
