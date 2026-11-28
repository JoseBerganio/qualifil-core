"""Organization, RBAC permission, scoping, and seeding tests (Sprint 02B)."""

from types import SimpleNamespace
import uuid

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView

from apps.accounts.models import Role, User
from apps.organizations import services
from apps.organizations.models import LGU, Barangay, OrganizationMembership
from apps.organizations.permissions import (
    HasOrganizationRole,
    IsBarangayOfficial,
    IsLGUAdmin,
    IsLGUPersonnel,
    IsResident,
    IsSystemAdmin,
    OrganizationScopedMixin,
    require_organization_roles,
)
from apps.organizations.selectors import (
    can_access_barangay,
    can_access_lgu,
    get_user_roles,
    scope_queryset_for_user,
    user_has_role,
)

pytestmark = pytest.mark.django_db

PASSWORD = "Str0ng!Passw0rd-2026"

LGUS_URL = "/api/v1/organizations/lgus/"
BARANGAYS_URL = "/api/v1/organizations/barangays/"
MEMBERSHIPS_URL = "/api/v1/organizations/memberships/"
MY_MEMBERSHIPS_URL = "/api/v1/organizations/memberships/me/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def org_tree():
    lgu_a = services.create_lgu(
        code="SILAY",
        name="City of Silay",
        province="Negros Occidental",
        region="Region VI",
    )
    lgu_b = services.create_lgu(
        code="TALISAY",
        name="City of Talisay",
        province="Negros Occidental",
        region="Region VI",
    )
    brgy_a1 = services.create_barangay(lgu=lgu_a, code="BRGY-1", name="Barangay I")
    brgy_a2 = services.create_barangay(lgu=lgu_a, code="BRGY-2", name="Barangay II")
    brgy_b1 = services.create_barangay(lgu=lgu_b, code="TAL-1", name="Zone 1")
    return SimpleNamespace(
        lgu_a=lgu_a,
        lgu_b=lgu_b,
        brgy_a1=brgy_a1,
        brgy_a2=brgy_a2,
        brgy_b1=brgy_b1,
    )


@pytest.fixture
def users(org_tree):
    sys_admin = User.objects.create_superuser(
        email="sysadmin@example.test",
        password=PASSWORD,
    )
    lgu_a_admin = User.objects.create_user(
        email="lgu.a.admin@example.test",
        password=PASSWORD,
    )
    lgu_a_staff = User.objects.create_user(
        email="lgu.a.staff@example.test",
        password=PASSWORD,
    )
    lgu_b_admin = User.objects.create_user(
        email="lgu.b.admin@example.test",
        password=PASSWORD,
    )
    brgy_a1_official = User.objects.create_user(
        email="brgy.a1@example.test",
        password=PASSWORD,
    )
    brgy_a2_official = User.objects.create_user(
        email="brgy.a2@example.test",
        password=PASSWORD,
    )
    resident = User.objects.create_user(
        email="resident@example.test",
        password=PASSWORD,
    )

    services.assign_membership(
        user=lgu_a_admin,
        role=Role.LGU_ADMIN,
        lgu=org_tree.lgu_a,
        assigned_by=sys_admin,
    )
    services.assign_membership(
        user=lgu_a_staff,
        role=Role.LGU_PERSONNEL,
        lgu=org_tree.lgu_a,
        assigned_by=lgu_a_admin,
    )
    services.assign_membership(
        user=lgu_b_admin,
        role=Role.LGU_ADMIN,
        lgu=org_tree.lgu_b,
        assigned_by=sys_admin,
    )
    services.assign_membership(
        user=brgy_a1_official,
        role=Role.BARANGAY_OFFICIAL,
        lgu=org_tree.lgu_a,
        barangay=org_tree.brgy_a1,
        assigned_by=lgu_a_admin,
    )
    services.assign_membership(
        user=brgy_a2_official,
        role=Role.BARANGAY_OFFICIAL,
        lgu=org_tree.lgu_a,
        barangay=org_tree.brgy_a2,
        assigned_by=lgu_a_admin,
    )

    return SimpleNamespace(
        sys_admin=sys_admin,
        lgu_a_admin=lgu_a_admin,
        lgu_a_staff=lgu_a_staff,
        lgu_b_admin=lgu_b_admin,
        brgy_a1_official=brgy_a1_official,
        brgy_a2_official=brgy_a2_official,
        resident=resident,
    )


# ---------------------------------------------------------------------------
# Models and membership invariants
# ---------------------------------------------------------------------------


def test_lgu_and_barangay_normalize_codes_and_enforce_uniqueness(org_tree):
    assert org_tree.lgu_a.code == "SILAY"
    assert org_tree.brgy_a1.code == "BRGY-1"

    with pytest.raises(ValidationError):
        LGU.objects.create(code="silay", name="Duplicate Silay")

    with pytest.raises(ValidationError):
        Barangay.objects.create(lgu=org_tree.lgu_a, code="brgy-1", name="Other Name")

    with pytest.raises(ValidationError):
        Barangay.objects.create(lgu=org_tree.lgu_a, code="BRGY-99", name="barangay i")


def test_membership_invariants_reject_invalid_role_or_barangay_scope(org_tree):
    candidate = User.objects.create_user(email="staff@example.test", password=PASSWORD)

    with pytest.raises(ValidationError):
        OrganizationMembership.objects.create(
            user=candidate,
            role=Role.RESIDENT,
            lgu=org_tree.lgu_a,
        )

    with pytest.raises(ValidationError):
        OrganizationMembership.objects.create(
            user=candidate,
            role=Role.BARANGAY_OFFICIAL,
            lgu=org_tree.lgu_a,
            barangay=None,
        )

    with pytest.raises(ValidationError):
        OrganizationMembership.objects.create(
            user=candidate,
            role=Role.BARANGAY_OFFICIAL,
            lgu=org_tree.lgu_a,
            barangay=org_tree.brgy_b1,
        )

    with pytest.raises(ValidationError):
        OrganizationMembership.objects.create(
            user=candidate,
            role=Role.LGU_PERSONNEL,
            lgu=org_tree.lgu_a,
            barangay=org_tree.brgy_a1,
        )


def test_assign_and_deactivate_membership_syncs_user_role(org_tree, users):
    candidate = User.objects.create_user(email="candidate@example.test", password=PASSWORD)
    assert candidate.role == Role.RESIDENT

    membership = services.assign_membership(
        user=candidate,
        role=Role.BARANGAY_OFFICIAL,
        lgu=org_tree.lgu_a,
        barangay=org_tree.brgy_a1,
        assigned_by=users.lgu_a_admin,
    )
    candidate.refresh_from_db()
    assert candidate.role == Role.BARANGAY_OFFICIAL
    assert user_has_role(
        candidate,
        Role.BARANGAY_OFFICIAL,
        barangay_id=org_tree.brgy_a1.id,
    )

    services.deactivate_membership(membership=membership, revoked_by=users.lgu_a_admin)
    candidate.refresh_from_db()
    assert candidate.role == Role.RESIDENT
    assert not user_has_role(
        candidate,
        Role.BARANGAY_OFFICIAL,
        barangay_id=org_tree.brgy_a1.id,
    )

    # Re-assigning reactivates the existing membership row cleanly.
    reactivated = services.assign_membership(
        user=candidate,
        role=Role.BARANGAY_OFFICIAL,
        lgu=org_tree.lgu_a,
        barangay=org_tree.brgy_a1,
        assigned_by=users.lgu_a_admin,
    )
    assert reactivated.id == membership.id
    assert reactivated.is_active is True


def test_staff_base_role_without_active_membership_has_no_org_access(org_tree):
    unassigned = User.objects.create_user(
        email="unassigned@example.test",
        password=PASSWORD,
        role=Role.BARANGAY_OFFICIAL,
    )
    assert Role.BARANGAY_OFFICIAL not in get_user_roles(unassigned)
    assert not can_access_barangay(unassigned, org_tree.brgy_a1.id)
    assert not can_access_lgu(unassigned, org_tree.lgu_a.id)

    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = unassigned
    assert IsBarangayOfficial().has_permission(request, APIView()) is False
    assert IsLGUPersonnel().has_permission(request, APIView()) is False
    assert IsLGUAdmin().has_permission(request, APIView()) is False


def test_inactive_org_blocks_membership_access(org_tree, users):
    assert can_access_barangay(users.brgy_a1_official, org_tree.brgy_a1.id)
    services.update_lgu(org_tree.lgu_a, actor=users.sys_admin, is_active=False)
    assert not can_access_barangay(users.brgy_a1_official, org_tree.brgy_a1.id)
    assert not can_access_lgu(users.lgu_a_admin, org_tree.lgu_a.id, roles=(Role.LGU_ADMIN,))


# ---------------------------------------------------------------------------
# Permission classes and query scoping
# ---------------------------------------------------------------------------


def test_permission_classes_enforce_roles_and_object_scope(org_tree, users):
    factory = APIRequestFactory()
    view = APIView()

    req_sys = factory.get("/")
    req_sys.user = users.sys_admin
    assert IsSystemAdmin().has_permission(req_sys, view) is True
    assert IsResident().has_permission(req_sys, view) is False

    req_res = factory.get("/")
    req_res.user = users.resident
    assert IsResident().has_permission(req_res, view) is True
    assert IsBarangayOfficial().has_permission(req_res, view) is False

    req_brgy = factory.get("/")
    req_brgy.user = users.brgy_a1_official
    assert IsBarangayOfficial().has_permission(req_brgy, view) is True
    assert IsBarangayOfficial().has_object_permission(req_brgy, view, org_tree.brgy_a1) is False
    view.org_barangay_lookup = "id"
    assert IsBarangayOfficial().has_object_permission(req_brgy, view, org_tree.brgy_a1) is True
    assert IsBarangayOfficial().has_object_permission(req_brgy, view, org_tree.brgy_a2) is False
    assert IsBarangayOfficial().has_object_permission(req_brgy, view, org_tree.brgy_b1) is False

    req_lgu_staff = factory.get("/")
    req_lgu_staff.user = users.lgu_a_staff
    view_lgu = APIView()
    view_lgu.org_lgu_lookup = "id"
    assert IsLGUPersonnel().has_permission(req_lgu_staff, view_lgu) is True
    assert IsLGUPersonnel().has_object_permission(req_lgu_staff, view_lgu, org_tree.lgu_a) is True
    assert IsLGUPersonnel().has_object_permission(req_lgu_staff, view_lgu, org_tree.lgu_b) is False
    assert IsLGUAdmin().has_permission(req_lgu_staff, view_lgu) is False

    req_lgu_admin = factory.get("/")
    req_lgu_admin.user = users.lgu_a_admin
    assert IsLGUAdmin().has_permission(req_lgu_admin, view_lgu) is True
    assert IsLGUAdmin().has_object_permission(req_lgu_admin, view_lgu, org_tree.lgu_a) is True
    assert IsLGUAdmin().has_object_permission(req_lgu_admin, view_lgu, org_tree.lgu_b) is False


def test_reusable_scope_queryset_and_mixin_isolate_data(org_tree, users):
    all_memberships = OrganizationMembership.objects.all()

    # Barangay official in A1 only sees A1 memberships.
    a1_scoped = scope_queryset_for_user(all_memberships, users.brgy_a1_official)
    assert set(a1_scoped.values_list("user_id", flat=True)) == {users.brgy_a1_official.id}

    # LGU personnel in LGU A sees all LGU A memberships (admin, staff, A1, A2), never LGU B.
    lgu_a_scoped = scope_queryset_for_user(all_memberships, users.lgu_a_staff)
    lgu_a_user_ids = set(lgu_a_scoped.values_list("user_id", flat=True))
    assert users.lgu_a_admin.id in lgu_a_user_ids
    assert users.brgy_a1_official.id in lgu_a_user_ids
    assert users.brgy_a2_official.id in lgu_a_user_ids
    assert users.lgu_b_admin.id not in lgu_a_user_ids

    # Resident and anonymous fail closed.
    assert scope_queryset_for_user(all_memberships, users.resident).count() == 0
    assert scope_queryset_for_user(all_memberships, SimpleNamespace(is_authenticated=False)).count() == 0

    # Reusable mixin + factory permission class work together on a view.
    class ScopedMembershipView(OrganizationScopedMixin, APIView):
        permission_classes = [require_organization_roles(Role.BARANGAY_OFFICIAL, Role.LGU_PERSONNEL)]
        queryset = OrganizationMembership.objects.all()

        def get_queryset(self):
            return self.scope_queryset(self.queryset)

        def get(self, request):
            return Response({"count": self.get_queryset().count()})

    factory = APIRequestFactory()
    drf_view = ScopedMembershipView.as_view()
    factory_req = factory.get("/")
    from rest_framework.test import force_authenticate

    force_authenticate(factory_req, user=users.brgy_a2_official)
    resp = drf_view(factory_req)
    assert resp.status_code == 200
    assert resp.data["count"] == 1


# ---------------------------------------------------------------------------
# API endpoints & cross-org isolation
# ---------------------------------------------------------------------------


def test_public_lgu_and_barangay_lists_hide_inactive_records(api_client, org_tree, users):
    inactive_lgu = services.create_lgu(
        code="INACTIVE",
        name="Inactive City",
        is_active=False,
        actor=users.sys_admin,
    )
    services.create_barangay(
        lgu=org_tree.lgu_a,
        code="BRGY-OFF",
        name="Inactive Brgy",
        is_active=False,
        actor=users.lgu_a_admin,
    )

    lgu_resp = api_client.get(LGUS_URL)
    assert lgu_resp.status_code == 200
    lgu_codes = {item["code"] for item in lgu_resp.data}
    assert {"SILAY", "TALISAY"} == lgu_codes
    assert inactive_lgu.code not in lgu_codes

    brgy_resp = api_client.get(f"{LGUS_URL}{org_tree.lgu_a.id}/barangays/")
    assert brgy_resp.status_code == 200
    brgy_codes = {item["code"] for item in brgy_resp.data}
    assert brgy_codes == {"BRGY-1", "BRGY-2"}


def test_lgu_creation_restricted_to_system_admin(api_client, users):
    payload = {"code": "BACOLOD", "name": "City of Bacolod"}

    assert api_client.post(LGUS_URL, payload, format="json").status_code == 401

    api_client.force_authenticate(user=users.lgu_a_admin)
    denied = api_client.post(LGUS_URL, payload, format="json")
    assert denied.status_code == 403
    assert denied.data["error"]["code"] == "FORBIDDEN"

    api_client.force_authenticate(user=users.sys_admin)
    created = api_client.post(LGUS_URL, payload, format="json")
    assert created.status_code == 201
    assert created.data["code"] == "BACOLOD"


def test_barangay_creation_and_update_enforces_lgu_isolation(api_client, org_tree, users):
    # LGU A admin can create in LGU A.
    api_client.force_authenticate(user=users.lgu_a_admin)
    created = api_client.post(
        BARANGAYS_URL,
        {"lgu_id": str(org_tree.lgu_a.id), "code": "BRGY-3", "name": "Barangay III"},
        format="json",
    )
    assert created.status_code == 201

    # LGU A admin cannot create or patch in LGU B.
    cross_create = api_client.post(
        BARANGAYS_URL,
        {"lgu_id": str(org_tree.lgu_b.id), "code": "TAL-2", "name": "Zone 2"},
        format="json",
    )
    assert cross_create.status_code == 403

    cross_patch = api_client.patch(
        f"{BARANGAYS_URL}{org_tree.brgy_b1.id}/",
        {"name": "Tampered"},
        format="json",
    )
    assert cross_patch.status_code == 403

    # LGU personnel (non-admin) and barangay official cannot create barangays.
    api_client.force_authenticate(user=users.lgu_a_staff)
    assert (
        api_client.post(
            BARANGAYS_URL,
            {"lgu_id": str(org_tree.lgu_a.id), "code": "BRGY-4", "name": "Barangay IV"},
            format="json",
        ).status_code
        == 403
    )


def test_membership_assignment_and_isolation_paths(api_client, org_tree, users):
    new_staff = User.objects.create_user(email="new.staff@example.test", password=PASSWORD)

    # Unauthenticated -> 401
    assert api_client.get(MEMBERSHIPS_URL).status_code == 401

    # Resident -> 403 on list and create
    api_client.force_authenticate(user=users.resident)
    assert api_client.get(MEMBERSHIPS_URL).status_code == 403
    assert (
        api_client.post(
            MEMBERSHIPS_URL,
            {
                "user_id": str(new_staff.id),
                "role": Role.BARANGAY_OFFICIAL,
                "lgu_id": str(org_tree.lgu_a.id),
                "barangay_id": str(org_tree.brgy_a1.id),
            },
            format="json",
        ).status_code
        == 403
    )

    # LGU A admin cannot assign staff into LGU B -> 403
    api_client.force_authenticate(user=users.lgu_a_admin)
    cross_assign = api_client.post(
        MEMBERSHIPS_URL,
        {
            "user_id": str(new_staff.id),
            "role": Role.BARANGAY_OFFICIAL,
            "lgu_id": str(org_tree.lgu_b.id),
            "barangay_id": str(org_tree.brgy_b1.id),
        },
        format="json",
    )
    assert cross_assign.status_code == 403

    # LGU A admin can assign staff into LGU A -> 201
    created = api_client.post(
        MEMBERSHIPS_URL,
        {
            "user_id": str(new_staff.id),
            "role": Role.BARANGAY_OFFICIAL,
            "lgu_id": str(org_tree.lgu_a.id),
            "barangay_id": str(org_tree.brgy_a1.id),
        },
        format="json",
    )
    assert created.status_code == 201
    membership_id = created.data["id"]

    # Barangay official in A2 cannot view A1 membership (IDOR) -> 403
    api_client.force_authenticate(user=users.brgy_a2_official)
    assert api_client.get(f"{MEMBERSHIPS_URL}{membership_id}/").status_code == 403

    # Barangay official in A1 can view A1 membership -> 200
    api_client.force_authenticate(user=users.brgy_a1_official)
    assert api_client.get(f"{MEMBERSHIPS_URL}{membership_id}/").status_code == 200

    # LGU B admin cannot deactivate LGU A membership -> 403
    api_client.force_authenticate(user=users.lgu_b_admin)
    assert api_client.post(f"{MEMBERSHIPS_URL}{membership_id}/deactivate/").status_code == 403

    # LGU A admin can deactivate it -> 200
    api_client.force_authenticate(user=users.lgu_a_admin)
    deactivated = api_client.post(f"{MEMBERSHIPS_URL}{membership_id}/deactivate/")
    assert deactivated.status_code == 200
    assert deactivated.data["is_active"] is False


def test_me_endpoints_include_active_memberships(api_client, org_tree, users):
    api_client.force_authenticate(user=users.brgy_a1_official)

    me_resp = api_client.get("/api/v1/auth/me/")
    assert me_resp.status_code == 200
    assert me_resp.data["role"] == Role.BARANGAY_OFFICIAL
    assert len(me_resp.data["memberships"]) == 1
    assert me_resp.data["memberships"][0]["lgu"]["code"] == "SILAY"
    assert me_resp.data["memberships"][0]["barangay"]["code"] == "BRGY-1"

    my_memberships = api_client.get(MY_MEMBERSHIPS_URL)
    assert my_memberships.status_code == 200
    assert len(my_memberships.data) == 1
    assert my_memberships.data[0]["role"] == Role.BARANGAY_OFFICIAL


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------


def test_seed_organizations_command_is_idempotent():
    call_command("seed_organizations")
    silay = LGU.objects.get(code="SILAY")
    assert silay.name == "City of Silay"
    assert silay.barangays.count() == 16

    # Running a second time creates no duplicates.
    call_command("seed_organizations")
    assert LGU.objects.filter(code="SILAY").count() == 1
    assert Barangay.objects.filter(lgu=silay).count() == 16
    assert uuid.UUID(str(silay.id)) == silay.id
