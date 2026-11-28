"""Serializers for LGUs, barangays, and organization memberships."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import Role

from .models import LGU, STAFF_ROLE_CHOICES, Barangay, OrganizationMembership

User = get_user_model()


class LguSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = LGU
        fields = ("id", "code", "name")
        read_only_fields = fields


class BarangaySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Barangay
        fields = ("id", "code", "name")
        read_only_fields = fields


class LguSerializer(serializers.ModelSerializer):
    class Meta:
        model = LGU
        fields = (
            "id",
            "code",
            "name",
            "province",
            "region",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class LguCreateUpdateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=150)
    province = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    region = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    is_active = serializers.BooleanField(required=False, default=True)


class LguPatchSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32, required=False)
    name = serializers.CharField(max_length=150, required=False)
    province = serializers.CharField(max_length=150, required=False, allow_blank=True)
    region = serializers.CharField(max_length=150, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)


class BarangaySerializer(serializers.ModelSerializer):
    lgu = LguSummarySerializer(read_only=True)

    class Meta:
        model = Barangay
        fields = (
            "id",
            "lgu",
            "code",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class BarangayCreateSerializer(serializers.Serializer):
    lgu_id = serializers.PrimaryKeyRelatedField(
        queryset=LGU.objects.all(),
        source="lgu",
    )
    code = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=150)
    is_active = serializers.BooleanField(required=False, default=True)


class BarangayPatchSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32, required=False)
    name = serializers.CharField(max_length=150, required=False)
    is_active = serializers.BooleanField(required=False)


class MembershipUserSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "full_name")
        read_only_fields = fields


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = MembershipUserSummarySerializer(read_only=True)
    lgu = LguSummarySerializer(read_only=True)
    barangay = BarangaySummarySerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = (
            "id",
            "user",
            "role",
            "lgu",
            "barangay",
            "is_active",
            "assigned_at",
            "updated_at",
        )
        read_only_fields = fields


class UserMembershipSummarySerializer(serializers.ModelSerializer):
    lgu = LguSummarySerializer(read_only=True)
    barangay = BarangaySummarySerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ("id", "role", "lgu", "barangay", "is_active", "assigned_at")
        read_only_fields = fields


class MembershipAssignSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source="user",
    )
    role = serializers.ChoiceField(choices=STAFF_ROLE_CHOICES)
    lgu_id = serializers.PrimaryKeyRelatedField(
        queryset=LGU.objects.all(),
        source="lgu",
    )
    barangay_id = serializers.PrimaryKeyRelatedField(
        queryset=Barangay.objects.all(),
        source="barangay",
        required=False,
        allow_null=True,
        default=None,
    )

    def validate(self, attrs):
        role = attrs["role"]
        lgu = attrs["lgu"]
        barangay = attrs.get("barangay")
        if role == Role.BARANGAY_OFFICIAL and barangay is None:
            raise serializers.ValidationError(
                {"barangay_id": "A barangay is required for barangay officials."}
            )
        if role != Role.BARANGAY_OFFICIAL and barangay is not None:
            raise serializers.ValidationError(
                {
                    "barangay_id": (
                        "LGU-level roles cannot be assigned to a specific barangay."
                    )
                }
            )
        if barangay is not None and barangay.lgu_id != lgu.id:
            raise serializers.ValidationError(
                {"barangay_id": "The selected barangay does not belong to the LGU."}
            )
        return attrs
