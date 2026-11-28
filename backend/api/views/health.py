"""Health-check endpoints (Sprint 01B)."""

import logging

from django.conf import settings
from django.core.cache import caches
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class LivenessView(APIView):
    """Lightweight liveness check that requires no external services."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "environment": getattr(settings, "APP_ENV", "unknown"),
                "version": getattr(settings, "APP_VERSION", ""),
            }
        )


class ReadinessView(APIView):
    """Readiness check for the services the backend depends on."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        checks = {
            "database": self._check_database(),
            "redis": self._check_redis(),
            "celery": self._check_celery(),
        }
        healthy = all(checks.values())
        return Response(
            {
                "status": "ok" if healthy else "degraded",
                "checks": checks,
            },
            status=(
                status.HTTP_200_OK
                if healthy
                else status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    def _check_database(self):
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception:
            logger.warning("Database health check failed", exc_info=True)
            return False

    def _check_redis(self):
        try:
            caches["default"].client.ping()
            return True
        except Exception:
            logger.warning("Redis health check failed", exc_info=True)
            return False

    def _check_celery(self):
        try:
            from config.celery import app as celery_app

            return bool(celery_app.control.inspect(timeout=1.0).ping())
        except Exception:
            logger.warning("Celery health check failed", exc_info=True)
            return False
