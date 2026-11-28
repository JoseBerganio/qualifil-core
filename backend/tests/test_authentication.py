"""Authentication API and service tests (Sprint 02A)."""

from datetime import timedelta

import pytest
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Role, User

pytestmark = pytest.mark.django_db

STRONG_PASSWORD = "Str0ng!Passw0rd-2026"
OTHER_PASSWORD = "An0ther!Passw0rd-2026"

REGISTER_URL = "/api/v1/auth/register/"
LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
ME_URL = "/api/v1/auth/me/"
CHANGE_PASSWORD_URL = "/api/v1/auth/change-password/"
CSRF_URL = "/api/v1/auth/csrf/"


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def client():
    test_client = APIClient(enforce_csrf_checks=True)
    test_client.raise_request_exception = True
    return test_client


@pytest.fixture
def user():
    return User.objects.create_user(
        email="resident@example.test",
        password=STRONG_PASSWORD,
        first_name="Test",
        last_name="Resident",
    )


def register_payload(**overrides):
    payload = {
        "email": "new.resident@example.test",
        "password": STRONG_PASSWORD,
        "first_name": "New",
        "last_name": "Resident",
        "phone_number": "09000000000",
    }
    payload.update(overrides)
    return payload


def login(client, *, email, password, mode=None, csrf_token=None):
    extra = {}
    if mode:
        extra["HTTP_X_AUTH_MODE"] = mode
    if csrf_token:
        extra["HTTP_X_CSRFTOKEN"] = csrf_token
    return client.post(
        LOGIN_URL,
        {"email": email, "password": password},
        format="json",
        **extra,
    )


def bearer_login(client, user):
    response = login(client, email=user.email, password=STRONG_PASSWORD)
    assert response.status_code == 200
    return response.data


def auth_header(tokens):
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens['access']}"}


def prime_csrf(client):
    response = client.get(CSRF_URL)
    assert response.status_code == 200
    token = response.data["csrfToken"]
    client.cookies[settings.CSRF_COOKIE_NAME] = token
    return token


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_creates_resident_and_returns_token_pair(client):
    response = client.post(REGISTER_URL, register_payload(), format="json")

    assert response.status_code == 201
    assert response.data["access"]
    assert response.data["refresh"]
    assert response.data["user"]["role"] == Role.RESIDENT
    assert response.data["user"]["email"] == "new.resident@example.test"

    created = User.objects.get(email="new.resident@example.test")
    assert created.check_password(STRONG_PASSWORD)
    assert created.password != STRONG_PASSWORD


def test_register_normalizes_email_and_rejects_case_insensitive_duplicates(client):
    first = client.post(
        REGISTER_URL,
        register_payload(email="MixedCase@Example.test"),
        format="json",
    )
    assert first.status_code == 201

    duplicate = client.post(
        REGISTER_URL,
        register_payload(email="mixedcase@example.TEST"),
        format="json",
    )
    assert duplicate.status_code == 409
    assert duplicate.data["error"]["code"] == "CONFLICT"
    assert User.objects.filter(email="mixedcase@example.test").count() == 1


def test_register_never_accepts_privileged_fields(client):
    response = client.post(
        REGISTER_URL,
        register_payload(role=Role.LGU_ADMIN, is_staff=True, is_superuser=True),
        format="json",
    )

    assert response.status_code == 201
    created = User.objects.get(email="new.resident@example.test")
    assert created.role == Role.RESIDENT
    assert created.is_staff is False
    assert created.is_superuser is False


def test_register_rejects_weak_password(client):
    response = client.post(
        REGISTER_URL,
        register_payload(password="12345678"),
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"]["code"] == "BAD_REQUEST"
    assert response.data["error"]["details"]
    assert not User.objects.filter(email="new.resident@example.test").exists()


def test_register_validates_required_fields(client):
    response = client.post(REGISTER_URL, {"email": "not-an-email"}, format="json")

    assert response.status_code == 400
    fields = {detail.get("field") for detail in response.data["error"]["details"]}
    assert "email" in fields
    assert "password" in fields


# ---------------------------------------------------------------------------
# Login and lockout
# ---------------------------------------------------------------------------


def test_login_succeeds_and_resets_failure_counter(client, user):
    user.failed_login_attempts = 4
    user.save(update_fields=["failed_login_attempts"])

    response = login(client, email=user.email, password=STRONG_PASSWORD)

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
    assert response.data["user"]["email"] == user.email
    user.refresh_from_db()
    assert user.failed_login_attempts == 0


def test_login_rejects_invalid_credentials_without_leaking_account_existence(client, user):
    wrong_password = login(client, email=user.email, password="Wrong!Passw0rd-2026")
    unknown_user = login(
        client,
        email="nobody@example.test",
        password="Wrong!Passw0rd-2026",
    )

    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.data["error"]["code"] == "UNAUTHENTICATED"
    assert unknown_user.data["error"]["code"] == "UNAUTHENTICATED"
    assert wrong_password.data["error"]["message"] == unknown_user.data["error"]["message"]


def test_login_locks_account_after_repeated_failures(client, user):
    for _ in range(settings.AUTH_MAX_FAILED_LOGIN_ATTEMPTS - 1):
        response = login(client, email=user.email, password="Wrong!Passw0rd-2026")
        assert response.status_code == 401

    locked = login(client, email=user.email, password="Wrong!Passw0rd-2026")
    assert locked.status_code == 429
    assert locked.data["error"]["code"] == "TOO_MANY_REQUESTS"

    correct_but_locked = login(client, email=user.email, password=STRONG_PASSWORD)
    assert correct_but_locked.status_code == 429

    user.refresh_from_db()
    assert user.locked_until is not None


def test_lockout_expires(client, user):
    user.locked_until = timezone.now() - timedelta(seconds=1)
    user.save(update_fields=["locked_until"])

    response = login(client, email=user.email, password=STRONG_PASSWORD)

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.locked_until is None


def test_inactive_user_cannot_log_in(client, user):
    user.is_active = False
    user.save(update_fields=["is_active"])

    response = login(client, email=user.email, password=STRONG_PASSWORD)

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Authenticated endpoints
# ---------------------------------------------------------------------------


def test_me_requires_authentication(client):
    response = client.get(ME_URL)

    assert response.status_code == 401
    assert response.data["error"]["code"] == "UNAUTHENTICATED"


def test_me_returns_current_user(client, user):
    tokens = bearer_login(client, user)

    response = client.get(ME_URL, **auth_header(tokens))

    assert response.status_code == 200
    assert response.data["id"] == str(user.pk)
    assert response.data["email"] == user.email
    assert response.data["role"] == Role.RESIDENT


# ---------------------------------------------------------------------------
# Refresh and logout
# ---------------------------------------------------------------------------


def test_refresh_rotates_token_and_blacklists_the_old_one(client, user):
    tokens = bearer_login(client, user)

    refreshed = client.post(
        REFRESH_URL,
        {"refresh": tokens["refresh"]},
        format="json",
    )
    assert refreshed.status_code == 200
    assert refreshed.data["access"]
    assert refreshed.data["refresh"]
    assert refreshed.data["refresh"] != tokens["refresh"]

    reused = client.post(
        REFRESH_URL,
        {"refresh": tokens["refresh"]},
        format="json",
    )
    assert reused.status_code == 401


def test_refresh_rejects_invalid_token(client):
    response = client.post(
        REFRESH_URL,
        {"refresh": "not-a-token"},
        format="json",
    )

    assert response.status_code == 401


def test_logout_blacklists_refresh_token(client, user):
    tokens = bearer_login(client, user)

    logout = client.post(
        LOGOUT_URL,
        {"refresh": tokens["refresh"]},
        format="json",
    )
    assert logout.status_code == 204

    reused = client.post(
        REFRESH_URL,
        {"refresh": tokens["refresh"]},
        format="json",
    )
    assert reused.status_code == 401


# ---------------------------------------------------------------------------
# Password change
# ---------------------------------------------------------------------------


def test_change_password_requires_current_password(client, user):
    tokens = bearer_login(client, user)

    response = client.post(
        CHANGE_PASSWORD_URL,
        {"current_password": "Wrong!Passw0rd-2026", "new_password": OTHER_PASSWORD},
        format="json",
        **auth_header(tokens),
    )

    assert response.status_code == 400
    assert response.data["error"]["code"] == "BAD_REQUEST"


def test_change_password_validates_new_password(client, user):
    tokens = bearer_login(client, user)

    response = client.post(
        CHANGE_PASSWORD_URL,
        {"current_password": STRONG_PASSWORD, "new_password": "12345678"},
        format="json",
        **auth_header(tokens),
    )

    assert response.status_code == 400
    assert response.data["error"]["details"]


def test_change_password_invalidates_existing_tokens(client, user):
    tokens = bearer_login(client, user)

    changed = client.post(
        CHANGE_PASSWORD_URL,
        {"current_password": STRONG_PASSWORD, "new_password": OTHER_PASSWORD},
        format="json",
        **auth_header(tokens),
    )
    assert changed.status_code == 204

    reused_refresh = client.post(
        REFRESH_URL,
        {"refresh": tokens["refresh"]},
        format="json",
    )
    assert reused_refresh.status_code == 401

    old_login = login(client, email=user.email, password=STRONG_PASSWORD)
    assert old_login.status_code == 401

    new_login = login(client, email=user.email, password=OTHER_PASSWORD)
    assert new_login.status_code == 200


# ---------------------------------------------------------------------------
# Cookie transport and CSRF
# ---------------------------------------------------------------------------


def test_csrf_endpoint_is_public_and_sets_cookie(client):
    response = client.get(CSRF_URL)

    assert response.status_code == 200
    assert response.data["csrfToken"]
    assert settings.CSRF_COOKIE_NAME in response.cookies


def test_cookie_login_requires_csrf(client, user):
    response = login(client, email=user.email, password=STRONG_PASSWORD, mode="cookie")

    assert response.status_code == 403
    assert response.data["error"]["code"] == "FORBIDDEN"


def test_cookie_login_sets_http_only_cookies_and_hides_tokens(client, user):
    csrf_token = prime_csrf(client)

    response = login(
        client,
        email=user.email,
        password=STRONG_PASSWORD,
        mode="cookie",
        csrf_token=csrf_token,
    )

    assert response.status_code == 200
    assert "access" not in response.data
    assert "refresh" not in response.data
    assert response.data["user"]["email"] == user.email

    access_cookie = response.cookies[settings.AUTH_COOKIE_ACCESS_NAME]
    refresh_cookie = response.cookies[settings.AUTH_COOKIE_REFRESH_NAME]
    assert access_cookie["httponly"] is True
    assert refresh_cookie["httponly"] is True


def test_cookie_authentication_allows_safe_requests(client, user):
    csrf_token = prime_csrf(client)
    login(
        client,
        email=user.email,
        password=STRONG_PASSWORD,
        mode="cookie",
        csrf_token=csrf_token,
    )

    response = client.get(ME_URL)

    assert response.status_code == 200
    assert response.data["email"] == user.email


def test_cookie_authentication_requires_csrf_for_unsafe_requests(client, user):
    csrf_token = prime_csrf(client)
    login(
        client,
        email=user.email,
        password=STRONG_PASSWORD,
        mode="cookie",
        csrf_token=csrf_token,
    )

    response = client.post(
        CHANGE_PASSWORD_URL,
        {"current_password": STRONG_PASSWORD, "new_password": OTHER_PASSWORD},
        format="json",
    )

    assert response.status_code == 403
    assert response.data["error"]["code"] == "FORBIDDEN"


def test_cookie_refresh_and_logout_rotate_and_clear_cookies(client, user):
    csrf_token = prime_csrf(client)
    login(
        client,
        email=user.email,
        password=STRONG_PASSWORD,
        mode="cookie",
        csrf_token=csrf_token,
    )

    refreshed = client.post(
        REFRESH_URL,
        {},
        format="json",
        HTTP_X_AUTH_MODE="cookie",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert refreshed.status_code == 200
    assert settings.AUTH_COOKIE_ACCESS_NAME in refreshed.cookies

    logout = client.post(
        LOGOUT_URL,
        {},
        format="json",
        HTTP_X_AUTH_MODE="cookie",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert logout.status_code == 204
    assert logout.cookies[settings.AUTH_COOKIE_ACCESS_NAME].value == ""


# ---------------------------------------------------------------------------
# Throttling
# ---------------------------------------------------------------------------


def test_login_is_throttled(client, monkeypatch):
    from rest_framework.throttling import ScopedRateThrottle

    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "login", "2/min")

    first = login(client, email="nobody@example.test", password="Wrong!Passw0rd-2026")
    second = login(client, email="nobody@example.test", password="Wrong!Passw0rd-2026")
    third = login(client, email="nobody@example.test", password="Wrong!Passw0rd-2026")

    assert first.status_code == 401
    assert second.status_code == 401
    assert third.status_code == 429
    assert third.data["error"]["code"] == "TOO_MANY_REQUESTS"


# ---------------------------------------------------------------------------
# User manager
# ---------------------------------------------------------------------------


def test_user_manager_normalizes_email_and_creates_superuser():
    created = User.objects.create_user(
        email="Some.User@Example.TEST",
        password=STRONG_PASSWORD,
    )
    superuser = User.objects.create_superuser(
        email="admin@example.test",
        password=STRONG_PASSWORD,
    )

    assert created.email == "some.user@example.test"
    assert created.role == Role.RESIDENT
    assert created.is_staff is False
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.role == Role.SYSTEM_ADMIN
    assert superuser.check_password(STRONG_PASSWORD)


def test_public_health_endpoint_stays_anonymous(client):
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.data["status"] == "ok"
