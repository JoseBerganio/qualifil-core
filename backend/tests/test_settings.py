"""Tests for the QUALIFIL Django settings (Sprint 01B)."""

import os

from django.conf import settings


def test_settings_module_loaded():
    assert os.environ["DJANGO_SETTINGS_MODULE"] == "config.settings.testing"


def test_installed_apps_contain_foundation_apps():
    for app in [
        "api",
        "apps.accounts",
        "apps.organizations",
        "apps.residents",
        "apps.programs",
        "apps.eligibility",
        "apps.documents",
        "apps.applications",
        "apps.reviews",
        "apps.distributions",
        "apps.audit",
        "apps.notifications",
    ]:
        assert app in settings.INSTALLED_APPS


def test_root_urlconf_exposes_api_v1():
    assert settings.ROOT_URLCONF == "config.urls"
    from django.urls import reverse

    assert reverse("health-liveness").startswith("/api/v1/health")
    assert reverse("health-readiness").startswith("/api/v1/health")


def test_api_error_handler_configured():
    assert settings.REST_FRAMEWORK["EXCEPTION_HANDLER"] == "api.errors.exception_handler"


def test_logging_middleware_configured():
    assert "api.logging.RequestIDMiddleware" in settings.MIDDLEWARE
    assert "api.logging.RequestLogMiddleware" in settings.MIDDLEWARE
