"""Organization and staff membership domain services."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.accounts.models import Role

from .models import (
    LGU,
    ROLE_PRIORITY,
    STAFF_ROLES,
    Barangay,
    OrganizationMembership,
)
from .selectors import can_access_lgu, is_system_admin


class OrganizationServiceError(Exception):
    """Base exception for organization domain failures."""


class OrganizationPermissionDenied(OrganizationServiceError):
    """Actor lacks permission for the requested organization operation."""


class OrganizationValidationError(OrganizationServiceError):
    """Organization data or membership assignment violates business rules."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class OrganizationConflict(OrganizationServiceError):
    """Requested resource conflicts with an existing organization record."""


def _sync_user_staff_role(user):
    """Keep ``user.role`` aligned with active staff memberships when applicable."""
    if user.role == Role.SYSTEM_ADMIN or user.is_superuser:
        return user

    active_roles = list(
        OrganizationMembership.objects.filter(
            user=user,
            is_active=True,
            lgu__is_active=True,
        ).values_list("role", flat=True)
    )
    if active_roles:
        next_role = max(active_roles, key=lambda r: ROLE_PRIORITY.get(r, 0))
    else:
        next_role = Role.RESIDENT

    if user.role != next_role:
        user.role = next_role
        user.save(update_fields=["role", "updated_at"])
    return user


def _assert_can_manage_lgu_memberships(actor, lgu):
    if actor is None:
        return
    if is_system_admin(actor):
        return
    if can_access_lgu(actor, lgu.id, roles=(Role.LGU_ADMIN,)):
        return
    raise OrganizationPermissionDenied(
        "You do not have permission to manage staff for this LGU."
    )


@transaction.atomic
def create_lgu(*, code, name, province="", region="", is_active=True, actor=None):
    if actor is not None and not is_system_admin(actor):
        raise OrganizationPermissionDenied(
            "Only system administrators can create LGUs."
        )
    normalized_code = (code or "").strip().upper()
    if LGU.objects.filter(code__iexact=normalized_code).exists():
        raise OrganizationConflict("An LGU with this code already exists.")

    lgu = LGU(
        code=normalized_code,
        name=name,
        province=province,
        region=region,
        is_active=is_active,
    )
    try:
        lgu.save()
    except DjangoValidationError as exc:
        raise OrganizationValidationError("; ".join(exc.messages)) from exc
    return lgu


@transaction.atomic
def update_lgu(lgu, *, actor=None, **fields):
    if actor is not None and not is_system_admin(actor):
        raise OrganizationPermissionDenied(
            "Only system administrators can update LGUs."
        )
    allowed = {"code", "name", "province", "region", "is_active"}
    for key, value in fields.items():
        if key in allowed:
            setattr(lgu, key, value)
    if "code" in fields:
        normalized_code = (lgu.code or "").strip().upper()
        if (
            LGU.objects.filter(code__iexact=normalized_code)
            .exclude(pk=lgu.pk)
            .exists()
        ):
            raise OrganizationConflict("An LGU with this code already exists.")
    try:
        lgu.save()
    except DjangoValidationError as exc:
        raise OrganizationValidationError("; ".join(exc.messages)) from exc
    return lgu


@transaction.atomic
def create_barangay(*, lgu, code, name, is_active=True, actor=None):
    _assert_can_manage_lgu_memberships(actor, lgu)
    normalized_code = (code or "").strip().upper()
    normalized_name = (name or "").strip()

    if Barangay.objects.filter(lgu=lgu, code__iexact=normalized_code).exists():
        raise OrganizationConflict(
            "A barangay with this code already exists in the LGU."
        )
    if Barangay.objects.filter(lgu=lgu, name__iexact=normalized_name).exists():
        raise OrganizationConflict(
            "A barangay with this name already exists in the LGU."
        )

    barangay = Barangay(
        lgu=lgu,
        code=normalized_code,
        name=normalized_name,
        is_active=is_active,
    )
    try:
        barangay.save()
    except DjangoValidationError as exc:
        raise OrganizationValidationError("; ".join(exc.messages)) from exc
    return barangay


@transaction.atomic
def update_barangay(barangay, *, actor=None, **fields):
    _assert_can_manage_lgu_memberships(actor, barangay.lgu)
    allowed = {"code", "name", "is_active"}
    for key, value in fields.items():
        if key in allowed:
            setattr(barangay, key, value)

    if (
        Barangay.objects.filter(lgu=barangay.lgu, code__iexact=barangay.code.strip())
        .exclude(pk=barangay.pk)
        .exists()
    ):
        raise OrganizationConflict(
            "A barangay with this code already exists in the LGU."
        )
    if (
        Barangay.objects.filter(lgu=barangay.lgu, name__iexact=barangay.name.strip())
        .exclude(pk=barangay.pk)
        .exists()
    ):
        raise OrganizationConflict(
            "A barangay with this name already exists in the LGU."
        )

    try:
        barangay.save()
    except DjangoValidationError as exc:
        raise OrganizationValidationError("; ".join(exc.messages)) from exc
    return barangay


@transaction.atomic
def assign_membership(*, user, role, lgu, barangay=None, assigned_by=None):
    """Assign (or reactivate) a staff membership for ``user`` in an organization."""
    _assert_can_manage_lgu_memberships(assigned_by, lgu)

    if role not in STAFF_ROLES:
        raise OrganizationValidationError(
            "Only staff roles can be assigned through organization memberships."
        )
    if not lgu.is_active:
        raise OrganizationValidationError(
            "Cannot assign memberships to an inactive LGU."
        )
    if barangay is not None:
        if not barangay.is_active:
            raise OrganizationValidationError(
                "Cannot assign memberships to an inactive barangay."
            )
        if barangay.lgu_id != lgu.id:
            raise OrganizationValidationError(
                "The selected barangay does not belong to the specified LGU."
            )

    existing = OrganizationMembership.objects.filter(
        user=user,
        lgu=lgu,
        barangay=barangay,
        role=role,
    ).first()
    if existing is not None:
        if existing.is_active:
            raise OrganizationConflict("This organization membership already exists.")
        existing.is_active = True
        existing.assigned_by = assigned_by
        existing.save()
        _sync_user_staff_role(user)
        return existing

    membership = OrganizationMembership(
        user=user,
        role=role,
        lgu=lgu,
        barangay=barangay,
        is_active=True,
        assigned_by=assigned_by,
    )
    try:
        membership.save()
    except DjangoValidationError as exc:
        raise OrganizationValidationError("; ".join(exc.messages)) from exc

    _sync_user_staff_role(user)
    return membership


@transaction.atomic
def deactivate_membership(*, membership, revoked_by=None):
    """Deactivate a staff membership and recalculate the user's staff role."""
    _assert_can_manage_lgu_memberships(revoked_by, membership.lgu)
    if membership.is_active:
        membership.is_active = False
        membership.save(update_fields=["is_active", "updated_at"])
        _sync_user_staff_role(membership.user)
    return membership
