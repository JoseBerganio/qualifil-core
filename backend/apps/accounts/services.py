"""Authentication domain services.

Views and serializers stay thin; credential verification, lockout accounting,
password validation, and token invalidation live here so they can be reused by
later sprints (resident registration, password reset, admin provisioning).
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Role, User

logger = logging.getLogger(__name__)

# A fixed hash used to equalize timing when an email address does not exist.
_DUMMY_PASSWORD_HASH = make_password("qualifil-dummy-password")


class AuthServiceError(Exception):
    """Base class for authentication domain errors."""


class InvalidCredentials(AuthServiceError):
    """The supplied email/password pair is not valid."""


class AccountLocked(AuthServiceError):
    """The account is temporarily locked after repeated failed logins."""

    def __init__(self, retry_after_seconds):
        self.retry_after_seconds = max(int(retry_after_seconds), 0)
        super().__init__("The account is temporarily locked.")


class EmailAlreadyRegistered(AuthServiceError):
    """An account with the supplied email address already exists."""


class PasswordValidationFailed(AuthServiceError):
    """The password does not satisfy the configured validators."""

    def __init__(self, messages):
        self.messages = list(messages)
        super().__init__(" ".join(self.messages))


def normalize_email(email):
    return User.objects.normalize_email(email)


def _validate_password_for_user(password, *, email="", first_name="", last_name=""):
    candidate = User(email=email, first_name=first_name, last_name=last_name)
    try:
        validate_password(password, user=candidate)
    except DjangoValidationError as exc:
        raise PasswordValidationFailed(exc.messages) from exc


@transaction.atomic
def register_user(
    *,
    email,
    password,
    first_name="",
    last_name="",
    phone_number="",
):
    """Create a resident account.

    Public registration always creates a ``RESIDENT`` user. Staff roles are
    never accepted from client input and must be assigned administratively.
    """

    normalized_email = normalize_email(email)
    _validate_password_for_user(
        password,
        email=normalized_email,
        first_name=first_name,
        last_name=last_name,
    )

    if User.objects.filter(email__iexact=normalized_email).exists():
        raise EmailAlreadyRegistered

    try:
        return User.objects.create_user(
            email=normalized_email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=Role.RESIDENT,
        )
    except IntegrityError as exc:
        raise EmailAlreadyRegistered from exc


def authenticate_user(*, email, password, request=None):
    """Verify credentials, enforcing lockout after repeated failures.

    The returned user is the authenticated account. Invalid, inactive, and
    unknown accounts all raise the same ``InvalidCredentials`` error so the
    endpoint does not reveal whether an email address is registered.
    """

    normalized_email = normalize_email(email)
    now = timezone.now()
    failure = None

    # Failures are recorded inside the transaction and raised afterwards so the
    # attempt counter and lockout timestamp are committed, not rolled back.
    with transaction.atomic():
        user = (
            User.objects.select_for_update()
            .filter(email__iexact=normalized_email)
            .first()
        )

        if user is None:
            # Perform a constant-ish password check to reduce timing leakage.
            check_password(password, _DUMMY_PASSWORD_HASH)
            failure = InvalidCredentials()
        elif user.locked_until and user.locked_until > now:
            remaining = (user.locked_until - now).total_seconds()
            failure = AccountLocked(retry_after_seconds=remaining)
        elif not user.is_active:
            failure = InvalidCredentials()
        elif user.check_password(password):
            update_fields = []
            if user.failed_login_attempts:
                user.failed_login_attempts = 0
                update_fields.append("failed_login_attempts")
            if user.locked_until:
                user.locked_until = None
                update_fields.append("locked_until")
            user.last_login = now
            update_fields.append("last_login")
            user.save(update_fields=update_fields)
            return user
        else:
            user.failed_login_attempts += 1

            if user.failed_login_attempts >= settings.AUTH_MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(
                    minutes=settings.AUTH_LOCKOUT_MINUTES
                )
                user.failed_login_attempts = 0
                user.save(update_fields=["failed_login_attempts", "locked_until"])
                failure = AccountLocked(
                    retry_after_seconds=settings.AUTH_LOCKOUT_MINUTES * 60
                )
            else:
                user.save(update_fields=["failed_login_attempts"])
                failure = InvalidCredentials()

    if failure is None:
        failure = InvalidCredentials()

    if isinstance(failure, AccountLocked):
        logger.warning(
            "Account temporarily locked after repeated failed logins",
            extra={"user_id": str(user.pk)},
        )

    raise failure


def issue_tokens_for_user(user):
    """Return a new access/refresh token pair for the user."""

    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def rotate_refresh_token(raw_refresh):
    """Validate a refresh token and rotate it according to SimpleJWT settings.

    Returns ``(access_token, refresh_token)``. The old refresh token is
    blacklisted when rotation is enabled.
    """

    serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
    try:
        serializer.is_valid(raise_exception=True)
    except TokenError as exc:
        raise InvalidCredentials from exc

    data = serializer.validated_data
    return data["access"], data.get("refresh")


def blacklist_refresh_token(raw_refresh):
    """Blacklist a refresh token, ignoring already-invalid tokens."""

    if not raw_refresh:
        return
    try:
        RefreshToken(raw_refresh).blacklist()
    except (TokenError, AttributeError):
        logger.info("Ignoring invalid refresh token during logout")


def blacklist_all_user_tokens(user):
    """Invalidate every outstanding refresh token for the user."""

    for outstanding in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding)


@transaction.atomic
def change_password(*, user, current_password, new_password):
    """Change a user's password and invalidate outstanding refresh tokens."""

    if not user.check_password(current_password):
        raise InvalidCredentials

    _validate_password_for_user(
        new_password,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    blacklist_all_user_tokens(user)
    return user
