"""Reusable DRF role permissions and organization-scoped view mixins."""

from rest_framework.permissions import BasePermission

from apps.accounts.models import Role

from .models import BARANGAY_SCOPED_ROLES, LGU_SCOPED_ROLES
from .selectors import (
    can_access_barangay,
    can_access_lgu,
    get_active_memberships,
    is_system_admin,
    scope_queryset_for_user,
)


def _resolve_attr(obj, lookup):
    """Resolve a dotted attribute path on ``obj``, returning None if absent."""
    if not lookup or obj is None:
        return None
    current = obj
    for part in lookup.split("."):
        current = getattr(current, part, None)
        if current is None:
            return None
    return current


class IsSystemAdmin(BasePermission):
    """Allow access only to active system administrators."""

    message = "System administrator access is required."

    def has_permission(self, request, view):
        return is_system_admin(request.user)


class IsResident(BasePermission):
    """Allow access only to active resident accounts."""

    message = "Resident account access is required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.role == Role.RESIDENT
        )

    def has_object_permission(self, request, view, obj):
        owner_lookup = getattr(view, "resident_user_lookup", None)
        if not owner_lookup:
            return True
        owner = _resolve_attr(obj, owner_lookup)
        return owner == request.user or owner == getattr(request.user, "id", None)


class IsBarangayOfficial(BasePermission):
    """Allow access to users holding an active barangay official assignment."""

    message = "Active barangay official authorization is required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        return (
            get_active_memberships(user)
            .filter(role=Role.BARANGAY_OFFICIAL, barangay__isnull=False)
            .exists()
        )

    def has_object_permission(self, request, view, obj):
        barangay_lookup = getattr(view, "org_barangay_lookup", "barangay_id")
        barangay_id = _resolve_attr(obj, barangay_lookup)
        if barangay_id is None:
            return False
        return can_access_barangay(
            request.user,
            barangay_id,
            allow_lgu_roles=False,
        )


class IsLGUPersonnel(BasePermission):
    """Allow access to active LGU personnel or LGU administrators."""

    message = "Active LGU personnel authorization is required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        return get_active_memberships(user).filter(role__in=LGU_SCOPED_ROLES).exists()

    def has_object_permission(self, request, view, obj):
        lgu_lookup = getattr(view, "org_lgu_lookup", "lgu_id")
        lgu_id = _resolve_attr(obj, lgu_lookup)
        if lgu_id is None:
            return False
        return can_access_lgu(request.user, lgu_id, roles=LGU_SCOPED_ROLES)


class IsLGUAdmin(BasePermission):
    """Allow access only to active LGU administrators."""

    message = "Active LGU administrator authorization is required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        return get_active_memberships(user).filter(role=Role.LGU_ADMIN).exists()

    def has_object_permission(self, request, view, obj):
        lgu_lookup = getattr(view, "org_lgu_lookup", "lgu_id")
        lgu_id = _resolve_attr(obj, lgu_lookup)
        if lgu_id is None:
            return False
        return can_access_lgu(request.user, lgu_id, roles=(Role.LGU_ADMIN,))


class HasOrganizationRole(BasePermission):
    """Configurable role- and organization-scoped permission class.

    Views can declare ``required_roles`` (or instantiate via
    ``require_organization_roles``) plus optional lookup paths:
    ``org_lgu_lookup``, ``org_barangay_lookup``, ``resident_user_lookup``, and
    ``allow_system_admin``.
    """

    required_roles: tuple[str, ...] = ()
    allow_system_admin: bool = False
    message = "You do not have permission to access this organizational resource."

    def _effective_roles(self, view):
        return tuple(getattr(view, "required_roles", self.required_roles))

    def _allow_system_admin(self, view):
        return bool(getattr(view, "allow_system_admin", self.allow_system_admin))

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False

        if self._allow_system_admin(view) and is_system_admin(user):
            return True

        roles = set(self._effective_roles(view))
        if not roles:
            return False

        if Role.SYSTEM_ADMIN in roles and is_system_admin(user):
            return True
        if Role.RESIDENT in roles and user.role == Role.RESIDENT:
            return True

        staff_roles = roles.intersection({*LGU_SCOPED_ROLES, *BARANGAY_SCOPED_ROLES})
        if not staff_roles:
            return False
        return get_active_memberships(user).filter(role__in=staff_roles).exists()

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False

        if self._allow_system_admin(view) and is_system_admin(user):
            return True

        roles = set(self._effective_roles(view))
        if Role.SYSTEM_ADMIN in roles and is_system_admin(user):
            return True

        resident_lookup = getattr(view, "resident_user_lookup", None)
        if (
            Role.RESIDENT in roles
            and user.role == Role.RESIDENT
            and resident_lookup is not None
        ):
            owner = _resolve_attr(obj, resident_lookup)
            if owner == user or owner == user.id:
                return True

        lgu_lookup = getattr(view, "org_lgu_lookup", "lgu_id")
        barangay_lookup = getattr(view, "org_barangay_lookup", "barangay_id")
        lgu_id = _resolve_attr(obj, lgu_lookup)
        barangay_id = _resolve_attr(obj, barangay_lookup)

        lgu_roles = tuple(roles.intersection(LGU_SCOPED_ROLES))
        if lgu_roles and lgu_id is not None and can_access_lgu(
            user, lgu_id, roles=lgu_roles
        ):
            return True

        barangay_roles = tuple(roles.intersection(BARANGAY_SCOPED_ROLES))
        if (
            barangay_roles
            and barangay_id is not None
            and can_access_barangay(
                user,
                barangay_id,
                allow_lgu_roles=False,
                barangay_roles=barangay_roles,
            )
        ):
            return True

        return False


def require_organization_roles(*roles, allow_system_admin=False):
    """Build a permission class enforcing the specified roles and org scope."""
    allowed_roles = tuple(roles)

    class _ConfiguredOrganizationRole(HasOrganizationRole):
        required_roles = allowed_roles

    _ConfiguredOrganizationRole.allow_system_admin = allow_system_admin
    _ConfiguredOrganizationRole.__name__ = (
        f"RequireRoles_{'_'.join(allowed_roles) or 'None'}"
    )
    return _ConfiguredOrganizationRole


class OrganizationScopedMixin:
    """Generic view / viewset mixin that applies organization queryset scoping."""

    org_lgu_field = "lgu_id"
    org_barangay_field = "barangay_id"
    org_lgu_roles = LGU_SCOPED_ROLES
    org_barangay_roles = BARANGAY_SCOPED_ROLES
    org_resident_user_field = None
    org_allow_system_admin = False

    def scope_queryset(self, queryset):
        return scope_queryset_for_user(
            queryset,
            self.request.user,
            lgu_field=self.org_lgu_field,
            barangay_field=self.org_barangay_field,
            lgu_roles=self.org_lgu_roles,
            barangay_roles=self.org_barangay_roles,
            resident_user_field=self.org_resident_user_field,
            allow_system_admin=self.org_allow_system_admin,
        )

    def get_queryset(self):
        return self.scope_queryset(super().get_queryset())
