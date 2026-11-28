"""Serializers for authentication requests and responses."""

from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        default="",
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    memberships = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "memberships",
            "is_active",
            "is_staff",
            "created_at",
        )
        read_only_fields = fields

    def get_memberships(self, obj):
        from apps.organizations.selectors import get_active_memberships
        from apps.organizations.serializers import UserMembershipSummarySerializer

        memberships = get_active_memberships(obj)
        return UserMembershipSummarySerializer(memberships, many=True).data
