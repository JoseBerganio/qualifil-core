"""Account identity models.

The custom user model is the authentication root for the platform. Business
roles are stored here as a base role; Sprint 02B adds organization memberships
that scope a user's access to a specific LGU and barangay.
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class Role(models.TextChoices):
    """Base account roles.

    ``RESIDENT`` is the only role that can be assigned through public
    self-registration. Staff roles are assigned by administrators or through
    organization memberships managed in Sprint 02B.
    """

    RESIDENT = "RESIDENT", "Resident"
    BARANGAY_OFFICIAL = "BARANGAY_OFFICIAL", "Barangay official"
    LGU_PERSONNEL = "LGU_PERSONNEL", "LGU personnel"
    LGU_ADMIN = "LGU_ADMIN", "LGU administrator"
    SYSTEM_ADMIN = "SYSTEM_ADMIN", "System administrator"


class UserManager(BaseUserManager):
    """Manager that normalizes email addresses as the login identifier."""

    use_in_migrations = True

    def normalize_email(self, email):
        email = (email or "").strip().lower()
        return BaseUserManager.normalize_email(email)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", Role.RESIDENT)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.SYSTEM_ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom QUALIFIL user identified by a case-insensitive email address."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("email address", unique=True, max_length=254)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.RESIDENT,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "user"
        verbose_name_plural = "users"
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
            ),
        ]

    def save(self, *args, **kwargs):
        self.email = type(self).objects.normalize_email(self.email)
        self.first_name = (self.first_name or "").strip()
        self.last_name = (self.last_name or "").strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return self.get_full_name()

    def get_full_name(self):
        return " ".join(part for part in (self.first_name, self.last_name) if part).strip()

    def get_short_name(self):
        return self.first_name or self.email

    @property
    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())
