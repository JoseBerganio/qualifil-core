"""Root URL configuration for the QUALIFIL backend."""

from django.contrib import admin
from django.urls import include, path

from api.views import handlers
from api.views.health import LivenessView, ReadinessView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include(
            [
                path(
                    "health/",
                    LivenessView.as_view(),
                    name="health-liveness",
                ),
                path(
                    "health/ready/",
                    ReadinessView.as_view(),
                    name="health-readiness",
                ),
                path("auth/", include("apps.accounts.urls")),
                path("organizations/", include("apps.organizations.urls")),
            ]
        ),
    ),
]

handler404 = handlers.not_found
handler500 = handlers.server_error
