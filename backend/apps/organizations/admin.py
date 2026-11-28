"""Django admin registrations for LGUs, barangays, and memberships."""

from django.contrib import admin

from .models import LGU, Barangay, OrganizationMembership


@admin.register(LGU)
class LGUAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "province", "region", "is_active", "created_at")
    list_filter = ("is_active", "region")
    search_fields = ("code", "name", "province")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "lgu", "is_active", "created_at")
    list_filter = ("lgu", "is_active")
    search_fields = ("code", "name", "lgu__name", "lgu__code")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "lgu",
        "barangay",
        "is_active",
        "assigned_at",
    )
    list_filter = ("role", "is_active", "lgu")
    search_fields = ("user__email", "lgu__name", "barangay__name")
    readonly_fields = ("id", "assigned_at", "updated_at")
