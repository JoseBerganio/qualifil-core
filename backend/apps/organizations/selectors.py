"""Reusable organization-scoped query selectors and authorization helpers."""

from django.db.models import Q

from apps.accounts.models import Role

from .models import (
    BARANGAY_SCOPED_ROLES,
    LGU_SCOPED_ROLES,
    OrganizationMembership,
)


def is_system_admin(user) -> bool:
    """Return True if the user is an active system administrator."""
    return bool(
        user
        and user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.role == Role.SYSTEM_ADMIN)
    )


def get_active_memberships(user):
    """Return active staff organization memberships for an active user."""
    if not user or not user.is_authenticated or not user.is_active:
        return OrganizationMembership.objects.none()

    return (
        OrganizationMembership.objects.filter(
            user=user,
            is_active=True,
            lgu__is_active=True,
        )
        .filter(Q(barangay__isnull=True) | Q(barangay__is_active=True))
        .select_related("lgu", "barangay")
    )


def get_user_roles(user) -> set[str]:
    """Return the effective roles held by the user.

    Staff roles require an active organization membership; having a staff value
    on ``user.role`` without an active assignment does not grant access.
    """
    if not user or not user.is_authenticated or not user.is_active:
        return set()

    roles = set(
        get_active_memberships(user).values_list("role", flat=True).distinct()
    )
    if is_system_admin(user):
        roles.add(Role.SYSTEM_ADMIN)
    if user.role == Role.RESIDENT:
        roles.add(Role.RESIDENT)
    return roles


def get_user_lgu_ids(user, *, roles=LGU_SCOPED_ROLES) -> set:
    """Return LGU UUIDs where the user holds an active matching membership."""
    if not user or not user.is_authenticated or not user.is_active:
        return set()

    return set(
        get_active_memberships(user)
        .filter(role__in=roles)
        .values_list("lgu_id", flat=True)
    )


def get_user_barangay_ids(user, *, roles=BARANGAY_SCOPED_ROLES) -> set:
    """Return barangay UUIDs where the user holds an active matching membership."""
    if not user or not user.is_authenticated or not user.is_active:
        return set()

    return set(
        get_active_memberships(user)
        .filter(role__in=roles, barangay__isnull=False)
        .values_list("barangay_id", flat=True)
    )


def user_has_role(
    user,
    *roles,
    lgu_id=None,
    barangay_id=None,
    allow_system_admin=False,
) -> bool:
    """Check whether ``user`` holds any of ``roles`` (optionally scoped)."""
    if not user or not user.is_authenticated or not user.is_active:
        return False

    if allow_system_admin and is_system_admin(user):
        return True

    if not roles:
        return False

    requested = set(roles)
    if Role.SYSTEM_ADMIN in requested and is_system_admin(user):
        return True

    if (
        Role.RESIDENT in requested
        and user.role == Role.RESIDENT
        and lgu_id is None
        and barangay_id is None
    ):
        return True

    memberships = get_active_memberships(user).filter(role__in=requested)
    if lgu_id is not None:
        memberships = memberships.filter(lgu_id=lgu_id)
    if barangay_id is not None:
        memberships = memberships.filter(
            Q(barangay_id=barangay_id)
            | Q(role__in=LGU_SCOPED_ROLES, barangay__isnull=True)
        )
    return memberships.exists()


def can_access_lgu(
    user,
    lgu_id,
    *,
    roles=LGU_SCOPED_ROLES,
    allow_system_admin=False,
) -> bool:
    """Return True if the user may access LGU-scoped resources for ``lgu_id``."""
    if not user or not user.is_authenticated or not user.is_active or not lgu_id:
        return False
    if allow_system_admin and is_system_admin(user):
        return True
    return lgu_id in get_user_lgu_ids(user, roles=roles)


def can_access_barangay(
    user,
    barangay_id,
    *,
    lgu_id=None,
    allow_lgu_roles=True,
    lgu_roles=LGU_SCOPED_ROLES,
    barangay_roles=BARANGAY_SCOPED_ROLES,
    allow_system_admin=False,
) -> bool:
    """Return True if the user may access barangay-scoped resources."""
    if not user or not user.is_authenticated or not user.is_active or not barangay_id:
        return False
    if allow_system_admin and is_system_admin(user):
        return True
    if barangay_id in get_user_barangay_ids(user, roles=barangay_roles):
        return True
    if allow_lgu_roles and lgu_id is not None:
        return lgu_id in get_user_lgu_ids(user, roles=lgu_roles)
    return False


def scope_queryset_for_user(
    queryset,
    user,
    *,
    lgu_field="lgu_id",
    barangay_field="barangay_id",
    lgu_roles=LGU_SCOPED_ROLES,
    barangay_roles=BARANGAY_SCOPED_ROLES,
    resident_user_field=None,
    allow_system_admin=False,
):
    """Filter a queryset to the organizational scope authorized for ``user``.

    Fails closed by returning ``queryset.none()`` when the user is anonymous,
    inactive, or lacks matching organizational assignments.
    """
    if not user or not user.is_authenticated or not user.is_active:
        return queryset.none()

    if allow_system_admin and is_system_admin(user):
        return queryset

    scope_filter = Q()
    has_scope = False

    if lgu_field and lgu_roles:
        lgu_ids = get_user_lgu_ids(user, roles=lgu_roles)
        if lgu_ids:
            scope_filter |= Q(**{f"{lgu_field}__in": lgu_ids})
            has_scope = True

    if barangay_field and barangay_roles:
        barangay_ids = get_user_barangay_ids(user, roles=barangay_roles)
        if barangay_ids:
            scope_filter |= Q(**{f"{barangay_field}__in": barangay_ids})
            has_scope = True

    if resident_user_field and user.role == Role.RESIDENT:
        scope_filter |= Q(**{resident_user_field: user})
        has_scope = True

    if not has_scope:
        return queryset.none()

    return queryset.filter(scope_filter).distinct()
