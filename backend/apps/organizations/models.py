"""LGU, barangay, and staff organization membership models."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone

from apps.accounts.models import Role

STAFF_ROLES = (
    Role.BARANGAY_OFFICIAL,
    Role.LGU_PERSONNEL,
    Role.LGU_ADMIN,
)

LGU_SCOPED_ROLES = (
    Role.LGU_PERSONNEL,
    Role.LGU_ADMIN,
)

BARANGAY_SCOPED_ROLES = (Role.BARANGAY_OFFICIAL,)

STAFF_ROLE_CHOICES = tuple((role.value, role.label) for role in STAFF_ROLES)

ROLE_PRIORITY = {
    Role.BARANGAY_OFFICIAL: 1,
    Role.LGU_PERSONNEL: 2,
    Role.LGU_ADMIN: 3,
}


class LGU(models.Model):
    """Local Government Unit (city or municipality) operating programs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=150)
    province = models.CharField(max_length=150, blank=True, default="")
    region = models.CharField(max_length=150, blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "LGU"
        verbose_name_plural = "LGUs"
        constraints = [
            models.UniqueConstraint(
                Lower("code"),
                name="organizations_lgu_code_ci_unique",
            ),
        ]

    def clean(self):
        self.code = (self.code or "").strip().upper()
        self.name = (self.name or "").strip()
        self.province = (self.province or "").strip()
        self.region = (self.region or "").strip()
        if not self.code:
            raise ValidationError({"code": "LGU code is required."})
        if not self.name:
            raise ValidationError({"name": "LGU name is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Barangay(models.Model):
    """Barangay belonging to an LGU."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lgu = models.ForeignKey(
        LGU,
        on_delete=models.PROTECT,
        related_name="barangays",
    )
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "barangay"
        verbose_name_plural = "barangays"
        constraints = [
            models.UniqueConstraint(
                "lgu",
                Lower("code"),
                name="organizations_barangay_lgu_code_ci_unique",
            ),
            models.UniqueConstraint(
                "lgu",
                Lower("name"),
                name="organizations_barangay_lgu_name_ci_unique",
            ),
        ]

    def clean(self):
        self.code = (self.code or "").strip().upper()
        self.name = (self.name or "").strip()
        if not self.code:
            raise ValidationError({"code": "Barangay code is required."})
        if not self.name:
            raise ValidationError({"name": "Barangay name is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.lgu.code})"


class OrganizationMembership(models.Model):
    """Associates a staff user with an LGU and, when applicable, a barangay."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(
        max_length=32,
        choices=STAFF_ROLE_CHOICES,
        db_index=True,
    )
    lgu = models.ForeignKey(
        LGU,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="memberships",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_memberships",
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-assigned_at"]
        verbose_name = "organization membership"
        verbose_name_plural = "organization memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lgu", "role"],
                condition=Q(barangay__isnull=True),
                name="organizations_membership_lgu_role_unique",
            ),
            models.UniqueConstraint(
                fields=["user", "lgu", "barangay", "role"],
                condition=Q(barangay__isnull=False),
                name="organizations_membership_brgy_role_unique",
            ),
        ]

    def clean(self):
        if self.role not in STAFF_ROLES:
            raise ValidationError(
                {"role": "Organization memberships only support staff roles."}
            )
        if not self.lgu_id:
            raise ValidationError({"lgu": "An LGU is required."})

        if self.role == Role.BARANGAY_OFFICIAL:
            if not self.barangay_id:
                raise ValidationError(
                    {"barangay": "A barangay is required for barangay officials."}
                )
            if self.barangay.lgu_id != self.lgu_id:
                raise ValidationError(
                    {"barangay": "The selected barangay does not belong to the LGU."}
                )
        elif self.barangay_id is not None:
            raise ValidationError(
                {
                    "barangay": (
                        "LGU-level roles cannot be restricted to a single barangay."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        scope = self.barangay.name if self.barangay_id else self.lgu.name
        return f"{self.user} — {self.role} ({scope})"
