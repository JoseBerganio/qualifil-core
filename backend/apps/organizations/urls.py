"""URL routes for organization and RBAC membership endpoints."""

from django.urls import path

from . import views

app_name = "organizations"

urlpatterns = [
    path("lgus/", views.LguListCreateView.as_view(), name="lgu-list-create"),
    path("lgus/<uuid:pk>/", views.LguDetailView.as_view(), name="lgu-detail"),
    path(
        "lgus/<uuid:lgu_id>/barangays/",
        views.LguBarangayListView.as_view(),
        name="lgu-barangay-list",
    ),
    path(
        "barangays/",
        views.BarangayListCreateView.as_view(),
        name="barangay-list-create",
    ),
    path(
        "barangays/<uuid:pk>/",
        views.BarangayDetailView.as_view(),
        name="barangay-detail",
    ),
    path(
        "memberships/",
        views.MembershipListCreateView.as_view(),
        name="membership-list-create",
    ),
    path(
        "memberships/me/",
        views.MyMembershipsView.as_view(),
        name="membership-me",
    ),
    path(
        "memberships/<uuid:pk>/",
        views.MembershipDetailView.as_view(),
        name="membership-detail",
    ),
    path(
        "memberships/<uuid:pk>/deactivate/",
        views.MembershipDeactivateView.as_view(),
        name="membership-deactivate",
    ),
]
