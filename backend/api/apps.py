"""App configuration for the API package."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"
    label = "api"
    verbose_name = "QUALIFIL API utilities"

    def ready(self):
        from . import checks  # noqa: F401
