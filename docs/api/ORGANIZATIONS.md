# QUALIFIL — Organizations & RBAC API Contract (v0.2.0 / Sprint 02B)

All endpoints are mounted under `/api/v1/organizations/`. Errors use the standard QUALIFIL envelope defined in `backend/api/errors.py`.

## 1. Roles and Organizational Scope

| Role | Assigned via | Scope |
|---|---|---|
| `RESIDENT` | Public self-registration | Self-owned records (`ResidentProfile` in Sprint 02D) |
| `BARANGAY_OFFICIAL` | `OrganizationMembership` | Single assigned `Barangay` within its `LGU` |
| `LGU_PERSONNEL` | `OrganizationMembership` | Single assigned `LGU` |
| `LGU_ADMIN` | `OrganizationMembership` | Single assigned `LGU` + staff/barangay management inside that LGU |
| `SYSTEM_ADMIN` | Administrative superuser/base role | Platform-wide LGU administration |

Having a staff `role` on `accounts.User` without an active `OrganizationMembership` (for an active LGU and, when applicable, active barangay) does **not** grant access to organization-scoped resources.

## 2. Endpoints

### `GET /api/v1/organizations/lgus/`
Public. Lists active LGUs ordered by name. `SYSTEM_ADMIN` callers may pass `?include_inactive=true`.

### `POST /api/v1/organizations/lgus/`
Requires `SYSTEM_ADMIN`. Creates an LGU (`code`, `name`, optional `province`, `region`, `is_active`). Duplicate codes return `409 CONFLICT`.

### `GET /api/v1/organizations/lgus/<id>/` & `PATCH /api/v1/organizations/lgus/<id>/`
`GET` is public for active LGUs. `PATCH` requires `SYSTEM_ADMIN`.

### `GET /api/v1/organizations/lgus/<lgu_id>/barangays/`
Public. Lists active barangays belonging to the specified active LGU.

### `GET /api/v1/organizations/barangays/` & `POST /api/v1/organizations/barangays/`
`GET` is public (optional `?lgu_id=<uuid>`) for active barangays in active LGUs.
`POST` requires `LGU_ADMIN` (for the target `lgu_id`) or `SYSTEM_ADMIN`. Cross-LGU creation returns `403 FORBIDDEN`.

### `GET /api/v1/organizations/barangays/<id>/` & `PATCH /api/v1/organizations/barangays/<id>/`
`GET` is public for active barangays. `PATCH` requires `LGU_ADMIN` scoped to the barangay's LGU, or `SYSTEM_ADMIN`.

### `GET /api/v1/organizations/memberships/me/`
Requires authentication. Returns the caller's active organization memberships.

### `GET /api/v1/organizations/memberships/`
Requires an active staff role (`BARANGAY_OFFICIAL`, `LGU_PERSONNEL`, `LGU_ADMIN`) or `SYSTEM_ADMIN`.
Queryset is automatically scoped:
- `BARANGAY_OFFICIAL`: only memberships in their assigned barangay.
- `LGU_PERSONNEL` / `LGU_ADMIN`: only memberships in their assigned LGU.
- `SYSTEM_ADMIN`: all memberships.
- `RESIDENT`: `403 FORBIDDEN`.

Supports optional filters: `lgu_id`, `barangay_id`, `role`, `is_active`.

### `POST /api/v1/organizations/memberships/`
Requires `LGU_ADMIN` (for the target `lgu_id`) or `SYSTEM_ADMIN`.
Body: `{ "user_id": "<uuid>", "role": "BARANGAY_OFFICIAL|LGU_PERSONNEL|LGU_ADMIN", "lgu_id": "<uuid>", "barangay_id": "<uuid|null>" }`.
- `BARANGAY_OFFICIAL` requires a `barangay_id` belonging to `lgu_id`.
- `LGU_PERSONNEL` and `LGU_ADMIN` require `barangay_id` to be omitted or `null`.
- Cross-LGU assignment returns `403 FORBIDDEN`.

### `GET /api/v1/organizations/memberships/<id>/`
Requires staff authorization and object-level scope matching the membership's barangay or LGU (`403 FORBIDDEN` on cross-barangay/cross-LGU IDOR attempts).

### `POST /api/v1/organizations/memberships/<id>/deactivate/`
Requires `LGU_ADMIN` scoped to the membership's LGU, or `SYSTEM_ADMIN`. Deactivates the membership and recalculates the user's base role.

## 3. Initial Organization Seeding

```sh
python backend/manage.py seed_organizations
```

Idempotently seeds **City of Silay** (`SILAY`) and its 16 barangays.
