"""Organization and staff membership API views."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.errors import BadRequest, Conflict, Forbidden
from apps.accounts.models import Role

from . import services
from .models import LGU, Barangay, OrganizationMembership
from .permissions import HasOrganizationRole, IsSystemAdmin
from .selectors import (
    get_active_memberships,
    is_system_admin,
    scope_queryset_for_user,
)
from .serializers import (
    BarangayCreateSerializer,
    BarangayPatchSerializer,
    BarangaySerializer,
    LguCreateUpdateSerializer,
    LguPatchSerializer,
    LguSerializer,
    MembershipAssignSerializer,
    OrganizationMembershipSerializer,
)


def _raise_for_service_error(exc):
    if isinstance(exc, services.OrganizationPermissionDenied):
        raise Forbidden(str(exc)) from exc
    if isinstance(exc, services.OrganizationConflict):
        raise Conflict(str(exc)) from exc
    if isinstance(exc, services.OrganizationValidationError):
        raise BadRequest(exc.message) from exc
    raise exc


class LguListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsSystemAdmin()]

    def get(self, request):
        queryset = LGU.objects.all()
        include_inactive = (
            request.query_params.get("include_inactive", "").lower() == "true"
        )
        if not (include_inactive and is_system_admin(request.user)):
            queryset = queryset.filter(is_active=True)
        return Response(LguSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = LguCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            lgu = services.create_lgu(
                actor=request.user,
                **serializer.validated_data,
            )
        except services.OrganizationServiceError as exc:
            _raise_for_service_error(exc)
        return Response(LguSerializer(lgu).data, status=status.HTTP_201_CREATED)


class LguDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsSystemAdmin()]

    def get(self, request, pk):
        queryset = LGU.objects.all()
        if not is_system_admin(request.user):
            queryset = queryset.filter(is_active=True)
        lgu = get_object_or_404(queryset, pk=pk)
        return Response(LguSerializer(lgu).data)

    def patch(self, request, pk):
        lgu = get_object_or_404(LGU, pk=pk)
        serializer = LguPatchSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            updated = services.update_lgu(
                lgu,
                actor=request.user,
                **serializer.validated_data,
            )
        except services.OrganizationServiceError as exc:
            _raise_for_service_error(exc)
        return Response(LguSerializer(updated).data)


class LguBarangayListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, lgu_id):
        lgu_qs = LGU.objects.all()
        if not is_system_admin(request.user):
            lgu_qs = lgu_qs.filter(is_active=True)
        lgu = get_object_or_404(lgu_qs, pk=lgu_id)
        barangays = (
            Barangay.objects.filter(lgu=lgu, is_active=True)
            .select_related("lgu")
            .order_by("name")
        )
        return Response(BarangaySerializer(barangays, many=True).data)


class BarangayListCreateView(APIView):
    required_roles = (Role.LGU_ADMIN,)
    allow_system_admin = True

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), HasOrganizationRole()]

    def get(self, request):
        queryset = Barangay.objects.select_related("lgu").filter(
            is_active=True,
            lgu__is_active=True,
        )
        lgu_id = request.query_params.get("lgu_id") or request.query_params.get("lgu")
        if lgu_id:
            queryset = queryset.filter(lgu_id=lgu_id)
        return Response(BarangaySerializer(queryset, many=True).data)

    def post(self, request):
        serializer = BarangayCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            barangay = services.create_barangay(
                actor=request.user,
                **serializer.validated_data,
            )
        except services.OrganizationServiceError as exc:
            _raise_for_service_error(exc)
        return Response(
            BarangaySerializer(barangay).data,
            status=status.HTTP_201_CREATED,
        )


class BarangayDetailView(APIView):
    required_roles = (Role.LGU_ADMIN,)
    allow_system_admin = True
    org_lgu_lookup = "lgu_id"

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), HasOrganizationRole()]

    def get(self, request, pk):
        queryset = Barangay.objects.select_related("lgu")
        if not is_system_admin(request.user):
            queryset = queryset.filter(is_active=True, lgu__is_active=True)
        barangay = get_object_or_404(queryset, pk=pk)
        return Response(BarangaySerializer(barangay).data)

    def patch(self, request, pk):
        barangay = get_object_or_404(Barangay.objects.select_related("lgu"), pk=pk)
        self.check_object_permissions(request, barangay)
        serializer = BarangayPatchSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            updated = services.update_barangay(
                barangay,
                actor=request.user,
                **serializer.validated_data,
            )
        except services.OrganizationServiceError as exc:
            _raise_for_service_error(exc)
        return Response(BarangaySerializer(updated).data)


class MyMembershipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = get_active_memberships(request.user)
        return Response(OrganizationMembershipSerializer(memberships, many=True).data)


class MembershipListCreateView(APIView):
    allow_system_admin = True

    def get_permissions(self):
        if self.request.method == "GET":
            self.required_roles = (
                Role.BARANGAY_OFFICIAL,
                Role.LGU_PERSONNEL,
                Role.LGU_ADMIN,
            )
        else:
            self.required_roles = (Role.LGU_ADMIN,)
        return [IsAuthenticated(), HasOrganizationRole()]

    def get(self, request):
        queryset = OrganizationMembership.objects.select_related(
            "user",
            "lgu",
            "barangay",
        )
        queryset = scope_queryset_for_user(
            queryset,
            request.user,
            lgu_field="lgu_id",
            barangay_field="barangay_id",
            allow_system_admin=True,
        )
        lgu_id = request.query_params.get("lgu_id")
        if lgu_id:
            queryset = queryset.filter(lgu_id=lgu_id)
        barangay_id = request.query_params.get("barangay_id")
        if barangay_id:
            queryset = queryset.filter(barangay_id=barangay_id)
        role = request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return Response(OrganizationMembershipSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = MembershipAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership = services.assign_membership(
                assigned_by=request.user,
                **serializer.validated_data,
            )
        except services.OrganizationServiceError as exc:
            _raise_for_service_error(exc)
        return Response(
            OrganizationMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )


class MembershipDetailView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationRole]
    required_roles = (
        Role.BARANGAY_OFFICIAL,
        Role.LGU_PERSONNEL,
        Role.LGU_ADMIN,
    )
    allow_system_admin = True
    org_lgu_lookup = "lgu_id"
    org_barangay_lookup = "barangay_id"

    def get(self, request, pk):
        membership = get_object_or_404(
            OrganizationMembership.objects.select_related("user", "lgu", "barangay"),
            pk=pk,
        )
        self.check_object_permissions(request, membership)
        return Response(OrganizationMembershipSerializer(membership).data)


class MembershipDeactivateView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationRole]
    required_roles = (Role.LGU_ADMIN,)
    allow_system_admin = True
    org_lgu_lookup = "lgu_id"

    def post(self, request, pk):
        membership = get_object_or_404(
            OrganizationMembership.objects.select_related("user", "lgu", "barangay"),
            pk=pk,
        )
        self.check_object_permissions(request, membership)
        try:
            updated = services.deactivate_membership(
                membership=membership,
                revoked_by=request.user,
            )
        except services.OrganizationServiceError as exc:
            _raise_for_service_error(exc)
        return Response(OrganizationMembershipSerializer(updated).data)
