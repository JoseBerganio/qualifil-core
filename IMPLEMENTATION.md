# IMPLEMENTATION.md — QUALIFIL Sprint-by-Sprint Engineering Guide

This guide translates every sprint and numbered implementation task in [SPRINT.md](SPRINT.md) into concrete engineering instructions anchored in the QUALIFIL codebase, [AGENTS.md](AGENTS.md), and the architecture/security/testing docs.

> **How to use this guide:**
> 1. Confirm sprint dependencies and status in [SPRINT.md](SPRINT.md) and [PROGRESS.md](PROGRESS.md).
> 2. Create the sprint branch from `main` (e.g., `sprint/02a-authentication`).
> 3. Follow the task-by-task implementation specs below while honoring [AGENTS.md](AGENTS.md).
> 4. Complete the sprint's **Testing** and **Acceptance Criteria** in [SPRINT.md](SPRINT.md), then update [PROGRESS.md](PROGRESS.md) and [CHANGELOG.md](CHANGELOG.md).

---

## Cross-Cutting Implementation Conventions

Before starting any sprint in `v0.2.0`–`v0.5.0`, keep these shared patterns consistent:

- **Backend app layout (`backend/apps/<app>/`):** Organize each non-trivial app into `models.py`, `services.py` (business logic & `transaction.atomic()`), `selectors.py` (read queries / org-scoped querysets, optional), `permissions.py`, `serializers.py`, `views.py`, `urls.py`, `tasks.py`, `admin.py`, and `migrations/`.
- **Backend URLs:** Include each app's `urls.py` under `api/v1/` in `backend/config/urls.py`.
- **Backend errors:** Raise DRF validation/API exceptions or `api.errors.APIError` subclasses (`BadRequest`, `Unauthorized`, `Forbidden`, `NotFound`, `Conflict`) so every error renders via `api.errors.exception_handler`.
- **Shared TS API client (`packages/api-client/src/`):** Add endpoint types and client methods here when shared between `web/` and `mobile/`, then run `npm run build -w @qualifil/api-client`.
- **i18n (`web/` & `mobile/`):** Add matching keys in `en.json`, `fil.json`, and `hil.json` for every UI sprint.

---

# v0.1.0 — Project Foundation *(Implemented Baseline)*

Sprints `01A`–`01E` are already implemented (see [PROGRESS.md](PROGRESS.md)). This section summarizes where each task lives so developers know what foundation is already in place.

## Sprint 01A — Project Structure and CI Foundation (`sprint/01a-project-structure`)
1. **Initialize repository:** Git repo with `LICENSE` (MIT) and `.gitignore`.
2. **Monorepo directory structure:** `backend/`, `ai-service/`, `packages/api-client/`, `web/`, `mobile/`, `docs/`.
3. **Initial documentation files:** `README.md`, `SPRINT.md`, `PROGRESS.md`, `CHANGELOG.md`, `docs/adr/0001-modular-monolith-and-ai-service.md`, `docs/architecture/{OVERVIEW,MODULES}.md`, `docs/security/SECURITY.md`, `docs/testing/TEST_STRATEGY.md`.
4. **GitHub Actions CI workflow:** `.github/workflows/ci.yml` running `backend-tests`, `ai-service-tests`, `web-checks`, and `mobile-checks`.
5. **PR and branch protection:** PRs target `main`; CI runs on `push` (`main`, `sprint/**`) and `pull_request` (`main`).
6. **Repository hygiene:** `.editorconfig`, `.gitignore`, `.prettierignore`, `.env.example`.
7. **Formatting and linting:** `.prettierrc`, root `package.json` `format` / `format:check` / `lint` scripts, ESLint configs in `packages/api-client`, `web`, and `mobile`.

## Sprint 01B — Backend Foundation (`sprint/01b-backend-foundation`)
1. **Django + DRF:** `backend/requirements/base.txt`, `backend/manage.py`, `backend/config/`.
2. **Modular settings:** `backend/config/settings/{base,development,testing}.py` loading root `.env` via `python-dotenv` (`override=False`).
3. **`/api/v1/` namespace:** Configured in `backend/config/urls.py`.
4. **PostgreSQL 18 + pgvector:** `_parse_database_url` in `base.py`, `backend/docker/init.sql` (`CREATE EXTENSION IF NOT EXISTS vector;`), and `api.checks.pgvector_extension_check` (`api.E001` / `api.W001`).
5. **Redis + Celery:** `django_redis` cache and `backend/config/celery.py` + `backend/api/tasks.py` (`api.tasks.probe`).
6. **Health-check endpoints:** `GET /api/v1/health/` (`LivenessView`) and `GET /api/v1/health/ready/` (`ReadinessView`) in `backend/api/views/health.py`.
7. **Standardized API error responses:** `backend/api/errors.py` (`exception_handler`, `error_payload`, `APIError` subclasses) + `backend/api/views/handlers.py` (404/500 JSON handlers).
8. **Structured request logging:** `backend/api/logging.py` (`JSONFormatter`, `RequestIDMiddleware`, `RequestLogMiddleware`).
9. **S3-compatible storage:** `django-storages[boto3]` configured in `backend/config/settings/base.py` (`STORAGES["default"]`).
10. **Docker & Compose:** `backend/Dockerfile` and `backend/docker-compose.yml` (`db`, `redis`, `ai`, `worker`, `web`).
11. **pytest + pytest-django:** Root `pytest.ini`, `backend/pytest.ini`, and `backend/tests/`.
12. **Backend CI:** `backend-tests` job in `.github/workflows/ci.yml` with `pgvector/pgvector:pg18` service container.

## Sprint 01C — AI Service Foundation (`sprint/01c-ai-service-foundation`)
1. **FastAPI app:** `ai-service/app/main.py` (`create_app()` factory).
2. **Modular layout:** `app/api/`, `app/core/`, `app/schemas/`, `app/services/providers/`.
3. **Environment settings:** `ai-service/app/core/config.py` (`Settings.from_env()`).
4. **Internal service auth:** `require_internal_api_key` in `ai-service/app/api/dependencies.py` (`X-Internal-API-Key` + `hmac.compare_digest`).
5. **Health & model-status endpoints:** `GET /health/live`, `GET /health/ready`, `GET /internal/v1/models/status`.
6. **Standardized schemas & errors:** `ServiceRequest` (`extra="forbid"`), `ServiceResponse`, `ErrorResponse` in `app/schemas/common.py` and `app/api/errors.py`.
7. **Docker integration:** `ai-service/Dockerfile` wired into `backend/docker-compose.yml`.
8. **AI service CI:** `ai-service-tests` job running `pytest -q` in `ai-service/tests/`.

## Sprint 01D — Web Application Foundation (`sprint/01d-web-foundation`)
1–10. **Vite + React + TS + Tailwind + shadcn/ui + Router + API client + i18n + Status page + CI:** Implemented in `web/` (`src/app/App.tsx`, `src/components/{Button,LanguageSwitcher}.tsx`, `src/lib/api/`, `src/lib/i18n/`, `src/pages/AppStatusPage.tsx`) using `@qualifil/api-client`. Note: Task 6 (OpenAPI type generation from backend schema) is ready to be wired once `drf-spectacular` is added to Django alongside feature endpoints.

## Sprint 01E — Mobile Application Foundation (`sprint/01e-mobile-foundation`)
1–10. **Expo SDK 58 + RN 0.88 + Navigation + Components + `@qualifil/api-client` + `tokenStorage` + i18n + ConnectivityScreen + CI:** Implemented in `mobile/` (`src/app/{App,navigation}.tsx`, `src/components/`, `src/lib/api/`, `src/lib/storage/tokenStorage.ts`, `src/lib/i18n/`, `src/screens/{Connectivity,Settings}Screen.tsx`).

---

# v0.2.0 — Authentication and Core Data Management

## Sprint 02A — Authentication (`sprint/02a-authentication`)
**Dependencies:** `01B` | **Primary Targets:** `backend/apps/accounts/`, `backend/config/settings/base.py`, `packages/api-client/`

1. **Implement the custom Django user model:**
   - Create `User(AbstractBaseUser, PermissionsMixin)` in `backend/apps/accounts/models.py` with UUID or BigAuto PK, unique normalized `email` (`USERNAME_FIELD = "email"`), optional `phone_number`, `first_name`, `last_name`, `is_active`, `is_staff`, `failed_login_attempts`, `locked_until`, `created_at`, `updated_at`.
   - Implement `UserManager` (`create_user`, `create_superuser`) normalizing email lowercase.
   - Set `AUTH_USER_MODEL = "accounts.User"` in `backend/config/settings/base.py` and generate the initial migration before any other app creates user FKs.
2. **Configure SimpleJWT:**
   - Add `djangorestframework-simplejwt>=5.4` (and `token_blacklist` app if using DB blacklisting) to `backend/requirements/base.txt`.
   - Configure `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = ["rest_framework_simplejwt.authentication.JWTAuthentication"]` and `DEFAULT_PERMISSION_CLASSES = ["rest_framework.permissions.IsAuthenticated"]` (override `permission_classes = [AllowAny]` explicitly on health, login, register, refresh views).
   - Configure `SIMPLE_JWT` lifetimes from `.env.example`: `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` (30), `JWT_REFRESH_TOKEN_LIFETIME_DAYS` (7), `ROTATE_REFRESH_TOKENS=True`, `BLACKLIST_AFTER_ROTATION=True`.
3. **Implement registration and login services:**
   - Create `backend/apps/accounts/services.py` with `register_user(...)` and `authenticate_user(...)`.
   - Registration validates email uniqueness, hashes password via `set_password()`, and defaults account role to resident (never trust client-supplied staff/admin roles during self-registration).
4. **Implement access and refresh token handling:**
   - Expose `POST /api/v1/auth/register/`, `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`.
   - Support two transport behaviors cleanly: JSON token response for mobile (`access`, `refresh`, `user`) and httpOnly cookie setting (`access` / `refresh` cookies with `HttpOnly`, `SameSite=Lax`, `Secure` when not `DEBUG`) for web browser sessions, or an explicit client-mode header/endpoint so web never stores JWTs in `localStorage` (matching `mobile/src/lib/storage/tokenStorage.ts` comment).
5. **Implement logout and token invalidation:**
   - Expose `POST /api/v1/auth/logout/` that blacklists the supplied/cookie refresh token via `RefreshToken(token).blacklist()` and clears auth cookies if present.
6. **Implement password validation and secure password hashing:**
   - Enforce Django's `AUTH_PASSWORD_VALIDATORS` (`validate_password(password, user=user)`) in registration and password-change serializers; rely on Django's PBKDF2/Argon2 password hashers.
7. **Implement login throttling and account lockout:**
   - Add DRF `ScopedRateThrottle` on auth endpoints (e.g., `login`, `register`) backed by Django cache (`LocMemCache` in tests, Redis in dev/prod).
   - Track consecutive failures on `User` (or cache/Redis key per email+IP); after N failures (e.g. 5), set `locked_until = now + timedelta(minutes=15)` and return `429 TOO_MANY_REQUESTS` or `403` with standardized error envelope without leaking whether the email exists on normal invalid credentials (`401 UNAUTHENTICATED`).
8. **Implement authenticated user information endpoints:**
   - Expose `GET /api/v1/auth/me/` (returns user profile summary, active role/org memberships once `02B` lands) and `POST /api/v1/auth/change-password/`.
9. **Establish authentication behavior for web and mobile clients:**
   - Update `@qualifil/api-client` with typed `login`, `register`, `refresh`, `logout`, `getMe` methods and optional 401 refresh-retry hook; ensure `credentials: "include"` option is supported for web cookie mode while mobile continues sending `Authorization: Bearer <token>`.

## Sprint 02B — Organizations and Role-Based Access Control (`sprint/02b-organizations-rbac`)
**Dependencies:** `02A` | **Primary Targets:** `backend/apps/organizations/`

1. **Implement LGU and barangay models:**
   - `LGU` model (`name`, `code`, `province`, `region`, `is_active`, timestamps) and `Barangay` model (`lgu` FK, `name`, `code`, `is_active`, unique `(lgu, code)` / `(lgu, name)`).
2. **Establish staff membership associations:**
   - `OrganizationMembership` model linking `user` (FK), `role` (choices), `lgu` (FK, nullable for system-wide admin if needed, required for LGU/barangay roles), `barangay` (FK, required for `BARANGAY_OFFICIAL`, null for LGU roles), `is_active`, `assigned_by`, `assigned_at`. Enforce model `clean()` invariants (e.g., barangay must belong to `lgu`).
3. **Define resident, barangay official, LGU personnel, and administrator roles:**
   - Define `Role` `TextChoices`: `RESIDENT`, `BARANGAY_OFFICIAL`, `LGU_PERSONNEL`, `LGU_ADMIN` (and `SYSTEM_ADMIN` if distinct). Store resident base role or derive effective roles via `OrganizationMembership` + `ResidentProfile`.
4. **Implement role-based permission classes:**
   - Create `backend/apps/organizations/permissions.py` with DRF `BasePermission` classes: `IsResident`, `IsApprovedResident`, `IsBarangayOfficial`, `IsLGUPersonnel`, `IsLGUAdmin`, and composite helpers (`HasOrganizationRole`). Never rely on `is_staff` alone for domain endpoints.
5. **Implement organization-scoped data access:**
   - Implement `scope_queryset_for_user(qs, user, lgu_field="lgu", barangay_field="barangay")` in `backend/apps/organizations/services.py` (or `selectors.py`) so barangay officials only see records in their `barangay_id` and LGU staff only see records in their `lgu_id`.
6. **Establish reusable authorization and query-scoping patterns:**
   - Provide an `OrganizationScopedMixin` / view helper and object-level permission checks (`has_object_permission`) that return `403`/`404` consistently on cross-barangay and cross-LGU IDOR attempts.
7. **Implement initial organization data seeding:**
   - Create management command `python backend/manage.py seed_organizations` (idempotent `update_or_create`) seeding Silay City (`LGU`) and its barangays (synthetic or official public barangay list).

## Sprint 02C — Audit Logging (`sprint/02c-audit-logging`)
**Dependencies:** `02B` | **Primary Targets:** `backend/apps/audit/`

1. **Implement the audit event model:**
   - `AuditEvent` in `backend/apps/audit/models.py`: `id` (UUID), `actor` (FK nullable for anonymous/system), `actor_role`, `lgu` (FK nullable), `barangay` (FK nullable), `action` (indexed string, e.g. `auth.login.succeeded`), `target_type`, `target_id`, `outcome` (`success`/`failure`), `request_id`, `ip_address`, `metadata` (`JSONField`), `created_at` (indexed).
   - Override `save()`/`delete()` or restrict permissions/manager so existing `AuditEvent` rows cannot be updated or deleted in application code.
2. **Implement centralized audit recording services:**
   - `record_audit_event(*, action, actor=None, target=None, lgu=None, barangay=None, request=None, outcome="success", metadata=None)` in `backend/apps/audit/services.py`. Extract `request_id` (`request.request_id`) and client IP safely.
3. **Establish metadata sanitization:**
   - Implement `sanitize_metadata(data)` recursively redacting/dropping sensitive keys (`password`, `token`, `secret`, `api_key`, `authorization`, `ocr_text`, `id_number`, `ssn`, etc.) and truncating oversized values. Test nested dicts/lists.
4. **Record authentication events:**
   - Call `record_audit_event` from `accounts.services` on registration, login success, login failure, account lockout, logout, and password change.
5. **Implement audit event retrieval for authorized LGU personnel:**
   - `GET /api/v1/audit-events/` restricted to `IsLGUAdmin` / authorized `IsLGUPersonnel`, strictly filtered to the caller's `lgu_id`, supporting filters (`action`, `actor_id`, `target_type`, `date_from`, `date_to`) and pagination.
6. **Establish conventions for recording sensitive operations:**
   - Document required audit actions in `backend/apps/audit/constants.py` (`Actions`) so all downstream sprints (`02D`, `02E`, `04F`, `05B`, `05C`) emit consistent action strings.

## Sprint 02D — Resident Registration and Profiles (`sprint/02d-resident-profile`)
**Dependencies:** `02C` | **Primary Targets:** `backend/apps/residents/`

1. **Implement resident profile models:**
   - `ResidentProfile` (OneToOne `user`, `lgu` FK, `barangay` FK, `approval_status`: `PENDING`/`APPROVED`/`REJECTED`, `reviewed_by`, `reviewed_at`, `rejection_reason`, demographic/household fields needed by eligibility rules such as `birth_date`, `civil_status`, `household_size`, `monthly_income`, `employment_status`, `is_indigent`, `is_pwd`, `is_senior_citizen`, `is_solo_parent`, `is_student`, `address_line`, timestamps).
   - `ResidentConsent` (or fields + history table) recording privacy notice version and consent timestamp.
2. **Implement resident registration services:**
   - `register_resident(...)` in `backend/apps/residents/services.py` inside `transaction.atomic()`: creates `User` (via `accounts.services`), creates `ResidentProfile` (`PENDING`), records `ResidentConsent`, and emits an audit event.
3. **Implement profile creation and editing:**
   - `GET/PATCH /api/v1/residents/me/` allowing authenticated residents to view/update their own profile fields; prevent residents from modifying `approval_status`, `lgu`, or unauthorized verification flags directly (changing barangay may require re-approval).
4. **Implement resident information validation:**
   - Serializer and domain validators for birth dates (non-future), non-negative income, valid household size (`>= 1`), and barangay belonging to the selected LGU.
5. **Implement consent and privacy notice recording:**
   - Require explicit `consent_accepted=True` and `privacy_notice_version` on resident registration; reject without consent (`400 BAD_REQUEST`). Provide `GET /api/v1/residents/privacy-notice/` if needed.
6. **Implement resident approval and rejection workflows:**
   - `approve_resident(profile, reviewer, notes)` and `reject_resident(profile, reviewer, reason)` in `residents/services.py`: validate reviewer belongs to the resident's `barangay`, record status/timestamp/reviewer, and emit audit log.
7. **Implement barangay resident management endpoints:**
   - `GET /api/v1/barangay/residents/` (filterable by `approval_status`, search), `GET /api/v1/barangay/residents/{id}/`, `POST .../approve/`, `POST .../reject/` using `IsBarangayOfficial` + barangay org scoping.
8. **Establish resident fact provenance:**
   - Create `ResidentFact` (or `fact_provenance` model/structure) tracking `(resident, fact_key, value, source: SELF_REPORTED | BARANGAY_VERIFIED | DOCUMENT_EXTRACTED, verified_by, verified_at)` so Sprint `03B`/`03C` knows which facts came from resident self-declaration vs. staff verification.

## Sprint 02E — Assistance Program Management (`sprint/02e-program-management`)
**Dependencies:** `02D` | **Primary Targets:** `backend/apps/programs/`

1. **Implement assistance program categories:**
   - `ProgramCategory` model (`slug`, `name`, `description`, `is_active`) supporting localized names/descriptions or structured translations.
2. **Implement assistance program models:**
   - `AssistanceProgram` (persistent identity across versions: `lgu` FK, `category` FK, `slug`, `code`, `status`: `DRAFT`/`PUBLISHED`/`ARCHIVED`, `current_published_version` FK nullable, `source_type`: `SEED`/`LGU_CUSTOM`, `is_lgu_modified`, timestamps).
3. **Implement eligibility criterion definitions:**
   - `EligibilityCriterion` attached to `ProgramVersion` (`fact_key`, `operator`, `expected_value` JSONField, `requirement_level`: `REQUIRED` | `PREFERRED`, `weight_order`, `label`, `description`, `missing_fact_prompt`).
4. **Implement documentary requirement definitions:**
   - `DocumentaryRequirement` attached to `ProgramVersion` (`document_type_code`, `title`, `description`, `is_mandatory`, `condition_note`, `validity_days`).
5. **Establish a structured eligibility criteria catalog:**
   - Define canonical `fact_key`s and allowed `operator`s (`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `exists`, `between`) in `programs/catalog.py` (shared with `eligibility`) so admins cannot invent invalid criterion types.
6. **Implement program creation and editing:**
   - Draft editing model: either `ProgramVersion(status=DRAFT/PUBLISHED/ARCHIVED, version_number, is_immutable)` where edits always happen on a `DRAFT` `ProgramVersion`. Expose LGU endpoints to create programs, edit draft details, criteria, and documentary requirements.
7. **Implement program publishing and archiving:**
   - `publish_program_version(program, actor)` validates at least basic metadata/criteria, freezes the draft `ProgramVersion` (`status=PUBLISHED`, `published_at`, `published_by`), updates `program.current_published_version`, and emits an audit event.
   - `archive_program(program, actor)` marks program `ARCHIVED` (excluded from new discovery/applications, preserved for past assessments/applications).
8. **Implement immutable published program versions:**
   - Block updates/deletes on any `ProgramVersion` (and its child `EligibilityCriterion` / `DocumentaryRequirement` rows) once `status == PUBLISHED`; to edit a published program, clone its latest published version into a new `DRAFT` `ProgramVersion` with `version_number + 1`.
9. **Implement program retrieval and filtering:**
   - Public/resident read endpoints (`GET /api/v1/programs/`, `GET /api/v1/programs/{id}/`) return only `PUBLISHED` versions within the resident's LGU scope, filterable by `category`, `search`, `lgu`. Staff endpoints return drafts + versions within their LGU.
10. **Establish program management permissions:**
    - Restrict create/edit/publish/archive to `IsLGUAdmin` (or designated `IsLGUPersonnel`) scoped to `program.lgu`.

## Sprint 02F — Web Authentication and Program Management UI (`sprint/02f-web-auth-programs`)
**Dependencies:** `02E` | **Primary Targets:** `packages/api-client/`, `web/src/`

1. **Implement staff login and logout screens:**
   - Add `/login` page with email/password validation, error banner mapping `ApiError`, and logout action in app shell header. Use cookie-backed auth (`credentials: "include"` in `@qualifil/api-client`), not `localStorage`.
2. **Implement authenticated application routing:**
   - Create `AuthProvider` calling `GET /api/v1/auth/me/` on boot; add `<ProtectedRoute allowedRoles={...}>` wrapper in `web/src/app/App.tsx` redirecting unauthenticated users to `/login` and unauthorized roles to a localized 403 view.
3. **Implement role-based frontend navigation:**
   - Build responsive sidebar/navbar showing Barangay queues for `BARANGAY_OFFICIAL`, Program Management (and later LGU Review/Audit) for `LGU_PERSONNEL` / `LGU_ADMIN`.
4. **Implement the resident approval queue:**
   - Page `/barangay/residents` listing pending/approved/rejected residents in the official's barangay with status filter tabs, search, and pagination.
5. **Implement resident approval and rejection interfaces:**
   - Resident detail drawer/page showing submitted profile & consent record, with Approve confirmation and Reject modal requiring a rejection reason.
6. **Implement assistance program listing:**
   - Page `/programs` listing LGU programs with category, status (`Draft`, `Published`, `Archived`), current version badge, and actions.
7. **Implement the program creation and editing interface:**
   - Form for creating programs and editing draft versions (title, category, description, benefits summary, documentary requirements list).
8. **Implement the eligibility criteria editor:**
   - Structured form builder driven by the backend criteria catalog (dropdowns for `fact_key`, `operator`, typed value input, `Required` / `Preferred` toggle) — no raw free-form rule code.
9. **Implement program publishing and archiving controls:**
   - Publish button (with confirmation dialog noting version immutability), "Create New Draft Version" for published programs, and Archive action.
10. **Add translations for all new interface elements:**
    - Populate `web/src/lib/i18n/locales/{en,fil,hil}.json` for auth, nav, resident approval, and program management screens; write Vitest tests verifying key parity across locales.

## Sprint 02G — Mobile Authentication and Resident Profile UI (`sprint/02g-mobile-auth-profile`)
**Dependencies:** `02E` | **Primary Targets:** `packages/api-client/`, `mobile/src/`

1. **Implement resident registration screens:**
   - Multi-step or clean scrollable registration form (email, password, name, LGU/barangay picker, core demographic fields, explicit privacy notice + consent checkbox).
2. **Implement login and logout screens:**
   - `LoginScreen` calling `POST /api/v1/auth/login/`, storing access & refresh tokens via `tokenStorage`, and logout clearing tokens + calling `/auth/logout/`.
3. **Integrate secure token storage:**
   - Extend `mobile/src/lib/storage/tokenStorage.ts` to store both `accessToken` and `refreshToken` in `expo-secure-store` (native) / memory fallback (web test), and wire 401 token refresh in `mobile/src/lib/api/client.ts`.
4. **Implement resident profile viewing and editing:**
   - `ProfileScreen` displaying resident details, fact verification status badges, and an edit form calling `PATCH /api/v1/residents/me/`.
5. **Implement the pending approval screen:**
   - Dedicated `PendingApprovalScreen` (and rejected state with reason display) shown when `approval_status !== "APPROVED"`, preventing access to restricted resident features until barangay approval.
6. **Implement assistance program browsing:**
   - `ProgramsScreen` listing published programs scoped to the resident's LGU with category chips and text search.
7. **Implement assistance program details:**
   - `ProgramDetailScreen` displaying full program description, eligibility criteria summary, and required documents list.
8. **Implement the language selector:**
   - Surface `LanguageSwitcher` (`en`, `fil`, `hil`) in auth/settings and add all new translation keys to `mobile/src/lib/i18n/locales/{en,fil,hil}.json`.

---

# v0.3.0 — Eligibility Assessment and Program Matching

## Sprint 03A — Knowledge Base and Program Seeding (`sprint/03a-seed-knowledge-base`)
**Dependencies:** `02E` | **Primary Targets:** `knowledge-base/`, `backend/apps/programs/`

1. **Define the `programs_seed.json` structure:**
   - Create `knowledge-base/programs_seed.json` and `knowledge-base/programs_seed.schema.json`. Each entry includes `seed_key`, `seed_version`, `lgu_code`, `category_slug`, `title`, `description`, `verification_status` (`VERIFIED` | `NEEDS_VERIFICATION`), `source_reference`, `criteria`, and `documentary_requirements`.
2. **Establish JSON schema validation:**
   - Add `jsonschema` to `backend/requirements/base.txt` and validate `programs_seed.json` against `programs_seed.schema.json` (checking allowed `fact_key`s and operators from `programs/catalog.py`).
3. **Prepare initial Silay City assistance program entries:**
   - Author accurate, non-fabricated entries for Silay City; tag any criterion/document list not yet officially confirmed as `NEEDS_VERIFICATION`.
4. **Include AICS Medical Assistance, AICS Financial Assistance, and applicable scholarship programs:**
   - Populate structured criteria and documentary requirements for AICS Medical, AICS Financial, and Silay City scholarship programs with clear verification annotations.
5. **Implement seed validation services:**
   - `validate_seed_payload(data)` in `backend/apps/programs/seeding.py` returning structured validation errors before any DB write.
6. **Implement database import and export commands:**
   - Management commands: `python backend/manage.py import_programs [--file ...] [--dry-run]` and `python backend/manage.py export_programs [--output ...]`.
7. **Implement seed synchronization and version tracking:**
   - Store `seed_key`, `seed_hash`, and `seed_version` on `AssistanceProgram`; skip unchanged records on re-import so imports are 100% idempotent.
8. **Establish protection for LGU-modified program records:**
   - If `program.is_lgu_modified` is `True` (set automatically whenever an LGU admin edits/publishes via UI/API), `import_programs` MUST NOT overwrite the program unless an explicit `--force` flag is passed; log skipped/protected records clearly.

## Sprint 03B — Eligibility Engine (`sprint/03b-eligibility-engine`)
**Dependencies:** `02E` | **Primary Targets:** `backend/apps/eligibility/engine/` (pure Python, zero Django/AI imports)

1. **Define eligibility evaluation types and result structures:**
   - Create frozen `@dataclass` types in `backend/apps/eligibility/engine/types.py`: `CriterionStatus` (`MET`, `UNMET`, `UNKNOWN`), `OverallEligibility` (`LIKELY_ELIGIBLE`, `INELIGIBLE`, `NEEDS_MORE_INFO`), `CriterionInput`, `FactValue` (value + verification/source metadata), `CriterionResult`, and `EvaluationResult` (including `engine_version`).
2. **Implement supported comparison operators:**
   - Pure operator functions (`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `exists`, `between`) with strict type validation (e.g., numeric comparisons convert `Decimal`/`int`/`float` safely; type mismatch raises/returns invalid configuration rather than silently coercing wrongly).
3. **Implement fact-to-criterion evaluation:**
   - Look up `criterion.fact_key` in resident facts map. Handle missing keys or `None` values explicitly.
4. **Implement the three-state result system (`Met`, `Unmet`, `Unknown`):**
   - If the required fact is missing/`None`/unusable -> `CriterionStatus.UNKNOWN` (never `UNMET`).
   - If the criterion evaluates true -> `MET`; false -> `UNMET`. Include machine-readable reason code and compared values.
5. **Implement overall eligibility determination:**
   - Combine criterion results deterministically:
     - Any `REQUIRED` criterion is `UNMET` -> `INELIGIBLE`.
     - All `REQUIRED` criteria are `MET` -> `LIKELY_ELIGIBLE` (record `PREFERRED` outcomes separately as score/advisory metadata, never failing eligibility).
     - Otherwise (no `REQUIRED` is `UNMET`, at least one `REQUIRED` is `UNKNOWN`) -> `NEEDS_MORE_INFO`.
6. **Implement required and preferred criterion handling:**
   - Ensure `PREFERRED` criteria return `MET`/`UNMET`/`UNKNOWN` individually and contribute to preference fulfillment counts without blocking `LIKELY_ELIGIBLE`.
7. **Establish engine versioning:**
   - Define `ENGINE_VERSION = "1.0.0"` (bump on any semantic rule change) and attach it to every `EvaluationResult`.
8. **Implement golden test cases for seeded programs:**
   - Add JSON/Python golden fixtures for AICS Medical, AICS Financial, and Scholarship scenarios (eligible, clearly ineligible, partial/unknown facts, boundary ages/incomes) plus `hypothesis` property-based tests (determinism, permutation invariance, no `Unknown -> Unmet` leakage).
9. **Enforce separation between eligibility logic and AI functionality:**
   - Add an architecture unit test asserting `apps.eligibility.engine` does not import `django`, `celery`, `httpx`, `requests`, or AI modules.

## Sprint 03C — Assessment Snapshots and API (`sprint/03c-assessment-snapshots`)
**Dependencies:** `03B`, `02D` | **Primary Targets:** `backend/apps/eligibility/`

1. **Implement the eligibility assessment model:**
   - `EligibilityAssessment` (`id` UUID, `resident` FK, `program` FK, `program_version` FK, `engine_version`, `overall_status`, `resident_facts_snapshot` JSONField, `rule_snapshot` JSONField, `created_by`, `created_at`).
   - `CriterionAssessmentResult` (`assessment` FK, `criterion_id`, `fact_key`, `operator`, `expected_value`, `observed_value`, `requirement_level`, `status` [`MET`/`UNMET`/`UNKNOWN`], `reason_code`).
2. **Store resident fact snapshots:**
   - Serialize the exact resident profile fields + confirmed session facts used at evaluation time into `resident_facts_snapshot` JSON.
3. **Store program version references:**
   - Link directly to the exact `PUBLISHED` `ProgramVersion` evaluated (never a mutable `DRAFT`).
4. **Store individual criterion results:**
   - Persist one `CriterionAssessmentResult` row per criterion in `transaction.atomic()`.
5. **Store overall assessment results:**
   - Persist `overall_status` plus summary counts (`met_count`, `unmet_count`, `unknown_count`, `preferred_met_count`).
6. **Record the eligibility engine version:**
   - Store `EvaluationResult.engine_version` on `EligibilityAssessment`.
7. **Implement assessment services:**
   - `run_assessment(resident, program_version, extra_facts=None, actor=None)` in `eligibility/services.py`: maps `ResidentProfile` + `extra_facts` to pure engine inputs, runs `evaluate_program(...)`, saves immutable snapshot, and logs audit event.
8. **Implement assessment retrieval endpoints:**
   - `POST /api/v1/assessments/` (requires approved resident or authorized staff), `GET /api/v1/assessments/`, `GET /api/v1/assessments/{id}/`. Enforce strict resident ownership and barangay/LGU scoping.
9. **Establish assessment immutability:**
   - Block `PUT`/`PATCH`/`DELETE` on assessment API endpoints and override model `save()`/`delete()` to prevent updates once persisted. Add tests changing `ResidentProfile` and publishing a new `ProgramVersion` and asserting old assessments return identical snapshots.

## Sprint 03D — AI Embedding and Reranking Service (`sprint/03d-ai-embed-rerank`)
**Dependencies:** `01C` | **Primary Targets:** `ai-service/`

1. **Implement model provider interfaces:**
   - Refine `EmbeddingProvider` and `RerankProvider` in `ai-service/app/services/providers/base.py` if needed (batching, metadata/dimensions, health state transitions: `not_loaded` -> `loading` -> `ready` / `unavailable`).
2. **Implement a deterministic fake AI provider for testing:**
   - Create `FakeEmbeddingProvider` (deterministic SHA-256 seeded normalized unit vector of configured dim, e.g. 1024) and `FakeRerankProvider` (deterministic lexical overlap/hash score) in `ai-service/app/services/providers/fake.py`. Enable via `AI_PROVIDER_MODE=fake` (default in tests).
3. **Integrate `Qwen/Qwen3-Embedding-0.6B`:**
   - Implement `QwenEmbeddingProvider` in `ai-service/app/services/providers/qwen_embedding.py` using `transformers` / `sentence-transformers` + `torch`, L2-normalizing output embeddings, configurable device (`EMBEDDING_DEVICE`), and lazy or lifespan loading.
4. **Integrate `Qwen/Qwen3-Reranker-0.6B`:**
   - Implement `QwenRerankerProvider` in `ai-service/app/services/providers/qwen_reranker.py` computing relevance scores for `(query, document)` pairs sorted descending.
5. **Implement model loading and inference management:**
   - Update `ModelRegistry` (`ai-service/app/services/model_registry.py`) to hold active provider instances, manage `load()`/`unload()` in FastAPI lifespan (configurable `AI_PRELOAD_MODELS=false` for fast dev/test startup), and guard concurrent inference/loading safely.
6. **Implement embedding API endpoints:**
   - `POST /internal/v1/embeddings` (protected by `require_internal_api_key`): accepts `texts: list[str]` (bounded max batch & char length) and `purpose` (`query` | `document`), returns `{vectors, model, revision, dimensions}`.
7. **Implement reranking API endpoints:**
   - `POST /internal/v1/rerank` (protected by `require_internal_api_key`): accepts `query: str`, `documents: list[{id, text}]`, `top_n: int | None`, returns sorted `{results: [{id, index, score}], model, revision}`.
8. **Implement model loading status and error handling:**
   - Update `GET /internal/v1/models/status` and `/health/ready` to reflect live provider states; return `503 SERVICE_UNAVAILABLE` via `ServiceError` if an inference endpoint is called while the model is `unavailable` or failed to load (never crash the FastAPI process).
9. **Establish model revision pinning:**
   - Add `EMBEDDING_MODEL_REVISION` and `RERANKER_MODEL_REVISION` env settings (documented in `.env.example`) passed to HuggingFace `from_pretrained(..., revision=...)` and returned in `/models/status` and responses.
10. **Validate the selected model inference and reranking procedures:**
    - Add unit/contract tests using `Fake*Provider` in CI (`pytest -q`) and a documented manual verification script/test (marked `@pytest.mark.slow` / `@pytest.mark.real_model`) demonstrating real Qwen embedding dimensions, normalization, and reranking behavior. Update `docs/api/AI_SERVICE.md`.

## Sprint 03E — Program Embedding Synchronization (`sprint/03e-program-embeddings`)
**Dependencies:** `03A`, `03D` | **Primary Targets:** `backend/apps/programs/`, `backend/api/ai_client.py` (or `programs/ai_client.py`)

1. **Implement the program embedding model:**
   - Add `pgvector` Python package (`pgvector>=0.3`) to `backend/requirements/base.txt`.
   - Create `ProgramEmbedding` model (`program_version` OneToOne/FK, `embedding` `VectorField(dimensions=1024)`, `source_text`, `source_hash` SHA-256, `model_name`, `model_revision`, `status` [`PENDING`/`READY`/`FAILED`/`STALE`], `error_message`, `updated_at`) + HNSW/IVFFlat index migration.
2. **Establish deterministic program serialization:**
   - Create `serialize_program_for_embedding(program_version)` producing a canonical, sorted-key text representation (title, category, description, target group, criterion labels, document titles) and compute `sha256` `source_hash`.
3. **Implement the internal AI service client:**
   - Create a shared backend HTTP client (`httpx`) reading `AI_SERVICE_BASE_URL`, `AI_SERVICE_API_KEY`, and `AI_SERVICE_TIMEOUT_SECONDS`, forwarding `X-Request-ID`, raising typed exceptions on timeout/5xx/4xx, and never leaking the key.
4. **Implement Celery embedding tasks:**
   - `sync_program_version_embedding.delay(program_version_id)` in `backend/apps/programs/tasks.py`: checks current `source_hash` + `model_revision`, calls `POST /internal/v1/embeddings`, and upserts `ProgramEmbedding` idempotently.
5. **Trigger embedding generation when programs are published or updated:**
   - Enqueue `sync_program_version_embedding` using `transaction.on_commit(...)` inside `publish_program_version` (never before commit, and never fail publishing if Celery/AI service is down).
6. **Implement retry and failure handling:**
   - Configure Celery exponential backoff retries (`max_retries=5`, `autoretry_for=(AIServiceTransientError,)`); on permanent failure, mark `ProgramEmbedding.status = FAILED` and store sanitized `error_message`.
7. **Implement stale embedding detection:**
   - Mark embeddings stale whenever `source_hash` differs from current serialized text, `model_revision` differs from active config, or `program_version.status != PUBLISHED`.
8. **Implement embedding reconciliation:**
   - Add management command / periodic task `reconcile_program_embeddings` scanning published versions with missing, stale, or failed embeddings and queueing sync tasks.
9. **Implement program vector search using pgvector:**
   - Implement `search_program_embeddings(query_vector, lgu_id, limit=20)` filtering `program_version__status=PUBLISHED`, `program__lgu_id=lgu_id`, and excluding `STALE`/`FAILED` embeddings, ordered by `CosineDistance`.
10. **Establish model revision and source hash tracking:**
    - Reject mixing vectors from mismatched `model_name`/`model_revision` during search and record both on every `ProgramEmbedding` row.

## Sprint 03F — Program Matching Pipeline (`sprint/03f-matching-pipeline`)
**Dependencies:** `03C`, `03E` | **Primary Targets:** `backend/apps/eligibility/`, `ai-service/`

1. **Implement the matching request and result models:**
   - `MatchingSession` (`id` UUID, `resident` FK, `raw_query_redacted`, `selected_category`, `extracted_facts` JSONField, `confirmed_facts` JSONField, `status` [`PENDING`/`AWAITING_CONFIRMATION`/`PROCESSING`/`COMPLETED`/`DEGRADED`/`FAILED`], `ai_degraded` bool, `celery_task_id`, timestamps) and `MatchingResultItem` (`session` FK, `program_version` FK, `assessment` FK, `semantic_score`, `rerank_score`, `rank_order`, `match_source`).
2. **Implement the AI-assisted needs extraction endpoint:**
   - Add `POST /internal/v1/extract-needs` in `ai-service` (protected by `require_internal_api_key`) returning structured candidate facts (from allowed `programs/catalog.py` keys only) + candidate category slugs with strict Pydantic schema (`ServiceRequest`/`ServiceResponse`).
3. **Implement privacy-conscious input preprocessing:**
   - In Django before calling `ai-service`, strip/redact direct PII patterns (emails, phone numbers, government ID numbers, street numbers/names) and enforce max length + prompt-injection boundary framing (treat resident text as untrusted data).
4. **Implement resident confirmation of extracted information:**
   - Do **not** feed unconfirmed AI-extracted facts directly into eligibility assessments. Return extracted candidate facts in `AWAITING_CONFIRMATION`; require `POST /api/v1/matching/sessions/{id}/confirm/` where the resident edits/confirms facts before assessment runs.
5. **Implement query embedding:**
   - Call `POST /internal/v1/embeddings` (`purpose="query"`) on the preprocessed need query inside the matching task/service.
6. **Implement pgvector candidate retrieval:**
   - Retrieve top-K published programs in the resident's LGU (filtered optionally by confirmed category) via `search_program_embeddings`.
7. **Integrate Qwen reranking:**
   - Pass top-K candidate program summaries + resident query to `POST /internal/v1/rerank` to reorder candidates by relevance; keep graceful degradation if reranking times out.
8. **Run deterministic eligibility assessment on matched programs:**
   - For each retrieved candidate program version, call `run_assessment(resident, program_version, extra_facts=confirmed_facts)` so every match carries an authoritative deterministic `EligibilityAssessment` (`Met`/`Unmet`/`Unknown`).
9. **Implement asynchronous matching tasks:**
   - Celery task `execute_matching_session(session_id)` running embedding -> pgvector -> rerank -> deterministic assessment, transitioning session status atomically.
10. **Implement matching status retrieval and polling:**
    - `POST /api/v1/matching/sessions/`, `POST /api/v1/matching/sessions/{id}/confirm/`, `GET /api/v1/matching/sessions/{id}/` (returns `status`, `ai_degraded`, and ordered `results` once complete). Enforce resident ownership.
11. **Implement a fallback matching mechanism when AI services are unavailable:**
    - If `ai-service` is unreachable/5xx/timed out, automatically fall back to deterministic category + keyword search on published LGU programs, set `ai_degraded=True`, and still run `run_assessment` on matched programs.
12. **Implement matching evaluation using a labelled dataset:**
    - Create synthetic evaluation dataset (`knowledge-base/matching_eval_dataset.json` or `backend/tests/fixtures/`) and test/script measuring Recall@K / MRR with mocked and optional real-model evaluation runs.

## Sprint 03G — Eligibility Explanations (`sprint/03g-explanations`)
**Dependencies:** `03C`, `03D` | **Primary Targets:** `ai-service/`, `backend/apps/eligibility/`

1. **Implement the AI explanation endpoint:**
   - Add `POST /internal/v1/explain-eligibility` in `ai-service` (protected by `X-Internal-API-Key`).
2. **Implement explanation request and response validation:**
   - Request accepts `program_title`, `overall_status`, `locale` (`en`/`fil`/`hil`), and structured `criteria_results` (`label`, `status`, `requirement_level`, `reason_code`) — **no raw PII**. Response returns `{summary, criterion_explanations: [{criterion_id, explanation}], disclaimer}` validated with `ServiceResponse`.
3. **Implement criterion-level explanations:**
   - Ensure every criterion in the assessment receives an explanation faithful to its exact `MET` / `UNMET` / `UNKNOWN` status.
4. **Implement deterministic explanation templates:**
   - Implement template renderers in `backend/apps/eligibility/explanations.py` for `en`, `fil`, and `hil` keyed by `(status, reason_code)` so accurate, non-promissory explanations always exist locally.
5. **Implement LLM explanation integration using Claude Haiku 5.5:**
   - Implement `AnthropicExplanationProvider` in `ai-service/app/services/providers/anthropic_explanation.py` using `ANTHROPIC_API_KEY` + `LLM_MODEL` (`claude-haiku-5-5`) with system prompt enforcing: no status overrides, no guarantee/approval claims, and required disclaimer. Add `FakeExplanationProvider` for tests.
   - Run a post-generation guardrail in Django/AI service checking for prohibited guarantee phrases (e.g., "guaranteed approved", "you will receive") and verifying criterion statuses are not contradicted; fall back to templates on violation.
6. **Implement fallback behavior when AI services are unavailable:**
   - On timeout, error, schema failure, or guardrail rejection, return deterministic template explanations with `source="template"` (`ai_degraded=True`).
7. **Implement explanation caching:**
   - Cache generated explanations in Redis / `EligibilityExplanation` model keyed by `(assessment_id, locale, engine_version)` so repeated views do not re-call Anthropic.
8. **Establish Filipino and Hiligaynon language review:**
   - Store all template strings and disclaimer copy in reviewable translation catalogs and include tests checking `en`, `fil`, and `hil` outputs and prohibited-phrase filters.

## Sprint 03H — Mobile Matching UI and LGU Rule Preview (`sprint/03h-mobile-matching-ui`)
**Dependencies:** `03F`, `03G` | **Primary Targets:** `packages/api-client/`, `mobile/src/`, `web/src/`, `backend/apps/eligibility/`

1. **Implement the resident needs input screen:**
   - Mobile `MatchNeedsScreen`: free-text need input (character limit + privacy reminder not to enter sensitive IDs) + submit button.
2. **Implement predefined assistance category selection:**
   - Category chips/cards allowing residents to browse/match without typing free-text (ensuring full usability during AI degradation).
3. **Implement the extracted information confirmation screen:**
   - `ConfirmFactsScreen`: displays AI-extracted candidate facts with editable toggles/inputs so the resident explicitly confirms or corrects facts before running eligibility.
4. **Implement the matching results screen:**
   - `MatchResultsScreen`: lists matched programs ordered by relevance + eligibility status badge (`Likely Eligible`, `Needs More Info`, `Ineligible`).
5. **Implement asynchronous result polling:**
   - Poll `GET /api/v1/matching/sessions/{id}/` with bounded interval + timeout + cancel-on-unmount cleanup and pull-to-refresh.
6. **Implement eligibility result cards:**
   - Reusable `EligibilityCard` displaying overall potential-eligibility status (never "Approved"), met/unmet/unknown counts, and disclaimer.
7. **Implement criterion-level assessment details:**
   - `AssessmentDetailScreen` rendering each criterion's `Met` / `Unmet` / `Unknown` indicator and localized explanation.
8. **Implement multilingual explanations:**
   - Pass active `locale` (`en`/`fil`/`hil`) when requesting explanations and render localized summaries/disclaimers.
9. **Implement the AI degradation indicator:**
   - Non-blocking banner informing the resident when AI semantic search or AI explanations fell back to category/template mode (`ai_degraded=True`).
10. **Implement the LGU rule preview endpoint and web interface:**
    - Backend: `POST /api/v1/programs/{id}/preview-eligibility/` (accessible to `IsLGUPersonnel`/`IsLGUAdmin` for their LGU) evaluates a draft or published `ProgramVersion` against synthetic sample facts using the pure eligibility engine **without creating `EligibilityAssessment` rows**.
    - Web: "Preview Rules" panel inside the Program Editor allowing staff to test edge cases live. Add tests verifying DB assessment count does not change on preview.

---

# v0.4.0 — Document Processing and Application Management

## Sprint 04A — Document Storage and Upload (`sprint/04a-document-upload`)
**Dependencies:** `02D` | **Primary Targets:** `backend/apps/documents/`, `backend/config/settings/base.py`

1. **Implement the document model and document type catalog:**
   - `DocumentType` catalog (`code`, `name`, `description`, `accepted_mime_types`, `is_active`) matching `DocumentaryRequirement.document_type_code`.
   - `ResidentDocument` model (`id` UUID, `resident` FK, `document_type` FK, `storage_key`, `original_filename_sanitized`, `content_type`, `size_bytes`, `sha256_checksum`, `ocr_status` [`PENDING`/`PROCESSING`/`COMPLETED`/`FAILED`], `validation_status` [`PENDING`/`VERIFIED`/`FLAGGED`/`UNKNOWN`], `review_status` [`UNREVIEWED`/`APPROVED`/`REJECTED`/`ESCALATED`], `encrypted_extracted_text` binary/encrypted text, `is_deleted`, timestamps).
2. **Integrate S3-compatible storage:**
   - Wire `default_storage` (`django-storages` `S3Boto3Storage` already configured in `base.py`) with private ACL (`AWS_DEFAULT_ACL = "private"`, `AWS_QUERYSTRING_AUTH = True`); add MinIO service to `backend/docker-compose.yml` for local dev and use `InMemoryStorage` / mocked S3 in unit tests.
3. **Implement file type and file size validation:**
   - Enforce `MAX_UPLOAD_SIZE_MB` (10 MB default) and `ALLOWED_UPLOAD_EXTENSIONS` (`pdf,jpg,jpeg,png`) from `.env.example` before reading whole streams into memory.
4. **Implement file content verification:**
   - Never trust client filenames or `Content-Type` headers alone. Inspect magic bytes (`python-magic` or pure-Python header checks + `Pillow.Image.verify()` for images and PDF header/parser validation) to ensure actual bytes match allowed types.
5. **Implement secure file naming and storage paths:**
   - Generate non-guessable object keys (`documents/{lgu_id}/{resident_id}/{uuid4()}.{ext}`) and ignore/strip client path traversal (`../`) from display names.
6. **Implement image preprocessing for metadata removal:**
   - Re-encode uploaded JPEG/PNG images via `Pillow` (`ImageOps.exif_transpose` then save without EXIF/GPS metadata) before storing to strip sensitive device/location metadata.
7. **Implement encrypted storage for sensitive extracted text:**
   - Encrypt `extracted_text` (and sensitive extracted PII fields) at rest using authenticated symmetric encryption (e.g., `cryptography.fernet.Fernet` keyed via dedicated `DOCUMENT_TEXT_ENCRYPTION_KEY` env var documented in `.env.example`) before saving to PostgreSQL.
8. **Implement document upload, retrieval, and deletion endpoints:**
   - `POST /api/v1/documents/` (multipart upload), `GET /api/v1/documents/`, `GET /api/v1/documents/{id}/`, `GET /api/v1/documents/{id}/download/` (short-lived presigned URL or authorized backend streaming), `DELETE /api/v1/documents/{id}/` (prevent deleting documents locked by submitted applications).
9. **Implement permission-checked document access:**
   - Enforce owner-only access for residents, barangay-scoped read access for `BARANGAY_OFFICIAL`, and LGU-scoped read access for authorized `LGU_PERSONNEL` on submitted/escalated applications; emit audit events on download/deletion.

## Sprint 04B — OCR Processing (`sprint/04b-ocr-pipeline`)
**Dependencies:** `04A` | **Primary Targets:** `backend/apps/documents/`, `backend/Dockerfile`

1. **Integrate Tesseract OCR:**
   - Add `pytesseract`, `Pillow`, `pdf2image` (or `pypdf` + `poppler-utils` / `pymupdf`) to `backend/requirements/base.txt`, and install `tesseract-ocr`, `tesseract-ocr-eng`, `tesseract-ocr-fil`, and `poppler-utils` in `backend/Dockerfile`. Read `TESSERACT_CMD` from `.env`.
2. **Configure English and Filipino OCR language support:**
   - Use `OCR_DEFAULT_LANGUAGE` (`eng`) and `OCR_ADDITIONAL_LANGUAGES` (`fil`) (`eng+fil` Tesseract lang string), with graceful check if additional traineddata is missing in test environments.
3. **Implement image preprocessing:**
   - Before OCR, apply deterministic `Pillow` / OpenCV preprocessing (grayscale conversion, DPI scaling, contrast normalization, light thresholding/deskew) without overwriting the stored clean original file.
4. **Implement PDF text extraction processing:**
   - For PDFs, extract embedded digital text first (`pypdf`) if readable; if scanned/empty (below character threshold), rasterize pages (bounded max pages, e.g. 10) and run Tesseract per page.
5. **Implement document extraction models:**
   - `DocumentExtraction` model (`document` OneToOne/FK, `ocr_engine_version`, `language_used`, `page_count`, `mean_confidence`, `encrypted_raw_text`, `extracted_fields` JSONField, `processing_duration_ms`, `error_code`, `error_message`, `created_at`).
6. **Implement document-specific field parsers:**
   - Pure Python regex/heuristic parsers per `document_type` (e.g., Barangay Clearance, Certificate of Indigency, Valid ID, Medical Abstract/Billing, School Registration) extracting candidate `full_name`, `issue_date`, `expiry_date`, `barangay_name`, `amount`, etc., tagged with confidence/status.
7. **Implement asynchronous OCR tasks using Celery:**
   - `process_document_ocr(document_id)` in `backend/apps/documents/tasks.py`, queued via `transaction.on_commit(...)` after upload. Make task idempotent (skip if checksum already processed unless forced) and bound retries on transient storage/worker errors.
8. **Implement OCR processing status and error handling:**
   - Transition `ResidentDocument.ocr_status` (`PENDING` -> `PROCESSING` -> `COMPLETED` or `FAILED`); catch corrupt files, timeouts, or missing Tesseract binaries cleanly so users see safe error codes (no stack traces).
9. **Establish an OCR evaluation dataset:**
   - Generate synthetic test images/PDFs (via `Pillow`/ReportLab in tests — never real resident IDs) covering clear, rotated, low-contrast, and multi-page inputs and measure character/field extraction accuracy.

## Sprint 04C — Document Validation (`sprint/04c-document-validation`)
**Dependencies:** `04B` | **Primary Targets:** `backend/apps/documents/`

1. **Implement document readability checks:**
   - Pure Python validator checking image resolution/blur/contrast metrics, OCR `mean_confidence`, and minimum extracted character count; return `FLAGGED` or `UNKNOWN` if unreadable.
2. **Implement required field completeness checks:**
   - Compare parsed `extracted_fields` against required fields defined per `document_type` (e.g., `full_name`, `issue_date`). Missing fields produce `UNKNOWN` or `FLAGGED` rather than claiming forgery.
3. **Implement extracted information consistency checks:**
   - Normalize and compare extracted `full_name` (case-folding, punctuation stripping, middle-initial tolerance, fuzzy threshold) and `barangay_name` against the resident's `ResidentProfile`. Mismatches set `FLAGGED` with clear reason codes.
4. **Implement document expiration and validity checks:**
   - Parse `issue_date` and `expiry_date` across common Philippine date formats (`YYYY-MM-DD`, `MM/DD/YYYY`, `Month DD, YYYY`); check against `DocumentaryRequirement.validity_days` or explicit expiration date.
5. **Implement document validation result records:**
   - `DocumentValidationResult` (`document` FK, `rule_version`, `overall_status` [`VERIFIED`/`FLAGGED`/`UNKNOWN`], `checks` JSONField list of `{check_code, status, message}`, `validated_at`).
6. **Implement document verification services:**
   - `validate_document(document)` in `documents/services.py` automatically triggered at the end of `process_document_ocr` (and re-runnable on profile update).
7. **Implement document validation retrieval endpoints:**
   - Expose validation checks on `GET /api/v1/documents/{id}/validation/` (and embedded summary on document detail) restricted to document owner and authorized reviewers.
8. **Establish the distinction between `verified`, `flagged`, and `unknown` results:**
   - Document and enforce in code/UI copy that `VERIFIED` means *automated readability and consistency checks passed* — **never** proof of physical/legal authenticity — and `UNKNOWN` (e.g. unparseable date) is never silently treated as a hard rejection.

## Sprint 04D — Requirement Gap Analysis and Action Plans (`sprint/04d-gap-action-plan`)
**Dependencies:** `03G`, `04C` | **Primary Targets:** `backend/apps/documents/`, `backend/apps/eligibility/`, `ai-service/`

1. **Implement deterministic requirement gap analysis:**
   - Pure/service-layer function `analyze_requirement_gaps(resident, program_version, assessment=None)` combining the latest `EligibilityAssessment` and `ResidentDocument`s against `ProgramVersion.documentary_requirements`.
2. **Identify unmet eligibility criteria:**
   - Collect all `UNMET` criteria from the deterministic assessment (`status == UNMET`).
3. **Identify unknown eligibility criteria:**
   - Collect all `UNKNOWN` criteria (`status == UNKNOWN`) with prompts explaining which profile facts need completion/verification.
4. **Identify missing documentary requirements:**
   - Compare `ProgramVersion.documentary_requirements` against the resident's non-deleted, non-expired `ResidentDocument`s matching `document_type_code`.
5. **Identify flagged documents:**
   - Highlight attached/matching documents whose `validation_status == FLAGGED` or `ocr_status == FAILED` or `review_status == REJECTED`.
6. **Implement requirement gap retrieval endpoints:**
   - `GET /api/v1/programs/{program_id}/gap-analysis/` (or `POST /api/v1/gap-analyses/`) returning deterministic gap items + mapped actions for the authenticated approved resident.
7. **Implement AI-assisted action plan generation:**
   - Add `POST /internal/v1/action-plan` in `ai-service` (protected by `X-Internal-API-Key`) taking deterministic gap codes + locale (`en`/`fil`/`hil`) and returning prioritized plain-language steps.
8. **Implement response validation and deterministic fallback templates:**
   - Validate AI output against Pydantic schema and assert every returned action references only gap IDs present in the deterministic gap input (preventing hallucinated program requirements); fall back to deterministic template steps per gap type when AI is unavailable or invalid.
9. **Implement action plan caching and regeneration:**
   - Cache action plans by hash of `(resident_id, program_version_id, assessment_id, document_state_hash, locale)` and invalidate automatically when resident facts, documents, or program version change.

## Sprint 04E — Application Submission and Status Tracking (`sprint/04e-applications`)
**Dependencies:** `04D` | **Primary Targets:** `backend/apps/applications/`

1. **Implement the application model:**
   - `Application` (`id` UUID, `reference_number` unique human-readable code, `resident` FK, `lgu` FK, `barangay` FK, `program` FK, `program_version` FK, `assessment_snapshot` FK, `gap_snapshot` JSONField, `status`, `submitted_at`, `withdrawn_at`, timestamps). Enforce uniqueness constraint preventing duplicate active applications by the same resident for the same active program cycle/program.
2. **Implement application-document associations:**
   - `ApplicationDocument` (`application` FK, `document` FK, `requirement` FK nullable / `document_type_code`, `attached_at`), ensuring unique `(application, document)` or per requirement slot.
3. **Implement application status history:**
   - `ApplicationStatusHistory` (`application` FK, `from_status`, `to_status`, `changed_by` FK, `reason`, `metadata` JSONField, `created_at`).
4. **Define allowed application state transitions:**
   - Implement an explicit state machine map in `applications/state_machine.py` (`DRAFT` -> `SUBMITTED` -> `BARANGAY_REVIEW` -> `RETURNED_FOR_RESUBMISSION` / `ESCALATED_TO_LGU` / `LGU_REVIEW` -> `SELECTED` / `NOT_SELECTED` -> `DISTRIBUTED` / `UNCLAIMED`; `WITHDRAWN` allowed from pre-decision states). Reject invalid transitions with `409 CONFLICT`.
5. **Implement application creation:**
   - `POST /api/v1/applications/` creates a `DRAFT` application for an approved resident and a `PUBLISHED` program in their LGU, linking a fresh or recent `EligibilityAssessment` snapshot.
6. **Implement document attachment and removal:**
   - `POST /api/v1/applications/{id}/documents/` and `DELETE /api/v1/applications/{id}/documents/{doc_id}/` allowed only while application is `DRAFT` or `RETURNED_FOR_RESUBMISSION`, verifying the resident owns the document.
7. **Implement application submission validation:**
   - `POST /api/v1/applications/{id}/submit/` inside `transaction.atomic()` with `select_for_update()`: verify resident is approved, program version is still active/published, all mandatory documentary requirements have attached documents (not failed/deleted), and required criteria aren't bypassed; lock attached documents from deletion.
8. **Implement application withdrawal:**
   - `POST /api/v1/applications/{id}/withdraw/` transitions allowed pre-final states to `WITHDRAWN`, records `ApplicationStatusHistory`, and emits audit log.
9. **Implement application status retrieval:**
   - `GET /api/v1/applications/`, `GET /api/v1/applications/{id}/`, `GET /api/v1/applications/{id}/history/` scoped strictly to the owning resident (or authorized barangay/LGU staff in `04F`/`05A`).
10. **Preserve assessment and requirement snapshots at submission:**
    - Capture `assessment_snapshot`, `program_version`, and `submitted_requirements_snapshot` JSON on submission so later program edits or profile edits never alter submitted application records.

## Sprint 04F — Barangay Document Review and Escalation (`sprint/04f-brgy-document-review`)
**Dependencies:** `04E`, `04C` | **Primary Targets:** `backend/apps/reviews/`, `web/src/`

1. **Implement document review records:**
   - `DocumentReview` (`id` UUID, `application` FK, `document` FK, `reviewer` FK, `decision` [`VERIFIED`/`REJECTED`/`ESCALATED`], `notes`, `escalation_reason`, `created_at`) and `ApplicationReview` / escalation metadata.
2. **Implement barangay document review services:**
   - Service functions in `backend/apps/reviews/services.py` using `transaction.atomic()` and `select_for_update()` on `Application`/`ResidentDocument` to prevent concurrent conflicting decisions.
3. **Implement document verification decisions:**
   - Barangay official marks attached document `VERIFIED` with optional reviewer note; updates `ResidentDocument.review_status`.
4. **Implement rejection and resubmission handling:**
   - Barangay official marks document `REJECTED` with mandatory reason -> transitions application to `RETURNED_FOR_RESUBMISSION` (if allowed) so the resident can attach a replacement document and resubmit.
5. **Implement escalation to LGU personnel:**
   - Official marks flagged/edge-case document or application `ESCALATED` with mandatory justification -> transitions application to `ESCALATED_TO_LGU` / `LGU_REVIEW` visible to LGU personnel.
6. **Implement review endpoints:**
   - `GET /api/v1/barangay/applications/`, `GET /api/v1/barangay/applications/{id}/`, `POST /api/v1/barangay/applications/{id}/documents/{doc_id}/review/`, `POST /api/v1/barangay/applications/{id}/forward/` (all gated by `IsBarangayOfficial` + barangay org scoping).
7. **Implement the web-based barangay review queue:**
   - Web pages `/barangay/reviews` and `/barangay/reviews/:id` displaying applicant profile summary, deterministic eligibility snapshot, OCR extraction & validation flags (with explicit disclaimer that OCR is advisory), private document preview/download, and Verify/Reject/Escalate controls + translations (`en`/`fil`/`hil`).
8. **Integrate review decisions with application status transitions:**
   - Automatically advance application status via `applications.state_machine` when all documents are verified/forwarded, rejected, or escalated, recording `ApplicationStatusHistory`.
9. **Record review actions in the audit system:**
   - Emit `audit.services.record_audit_event` for every document verification, rejection, forwarding, and LGU escalation.

## Sprint 04G — Mobile Document and Application UI (`sprint/04g-mobile-documents-apps`)
**Dependencies:** `04D`, `04E` | **Primary Targets:** `packages/api-client/`, `mobile/src/`

1. **Implement requirement gap screens:**
   - `RequirementGapsScreen` showing met/unmet/unknown criteria and missing/flagged documents for a chosen program.
2. **Implement action plan screens:**
   - `ActionPlanScreen` rendering prioritized actionable checklist items (with AI/template source badge).
3. **Implement camera and gallery document uploads:**
   - Install `expo-image-picker` and `expo-document-picker` in `mobile/package.json` (root `npm install`); allow capturing photo or picking image/PDF and uploading via multipart `FormData` helper in `@qualifil/api-client` / `mobile/src/lib/api/`.
4. **Implement upload progress and retry handling:**
   - Show upload progress indicator, client-side size/extension pre-check (mirroring backend limits), and one-tap retry on transient network failure.
5. **Implement document processing status indicators:**
   - Poll document status until `ocr_status` leaves `PENDING`/`PROCESSING` and render badges (`Processing`, `Checks Passed`, `Flagged — Review Recommended`, `Failed`).
6. **Implement document reuse selection:**
   - `DocumentVaultScreen` / picker modal letting residents attach an already-uploaded valid `ResidentDocument` of the matching type instead of re-uploading.
7. **Implement application submission review screens:**
   - `ApplicationReviewScreen` summarizing program version, eligibility snapshot, attached documents, and confirmation submit button.
8. **Implement application history and status timelines:**
   - `ApplicationsListScreen` and `ApplicationDetailScreen` displaying `ApplicationStatusHistory` timeline, returned-document feedback, and Withdraw button.
9. **Implement slow network and error states:**
   - Offline/timeout states, pull-to-refresh, disabled duplicate submit buttons while inflight, and localized error messages (`en`, `fil`, `hil`).

---

# v0.5.0 — LGU Review and System Integration

## Sprint 05A — Applicant Review List (`sprint/05a-applicant-review-list`)
**Dependencies:** `04F` | **Primary Targets:** `backend/apps/reviews/`, `web/src/`

1. **Establish the applicant review module:**
   - Add LGU review selectors/views in `backend/apps/reviews/` (`lgu_views.py` / `selectors.py`) strictly enforcing `IsLGUPersonnel` / `IsLGUAdmin` + `lgu_id` scoping.
2. **Implement applicant grouping based on approved eligibility and document readiness criteria:**
   - Group submitted/forwarded/escalated applicants into clear, **non-weighted** categories: e.g., `READY_FOR_SELECTION` (all required criteria `MET` + all documents `VERIFIED`), `NEEDS_VERIFICATION` (contains `UNKNOWN` criteria or `ESCALATED`/`FLAGGED` documents), `INELIGIBLE_SUBMITTED` (if any `UNMET` required criterion exists). **Do NOT compute hidden ranking weights or AI scores.**
3. **Implement the applicant review query services:**
   - Optimize queries with `select_related` / `prefetch_related` (`resident__user`, `barangay`, `program_version`, `assessment_snapshot`, `documents`) to avoid N+1 queries.
4. **Implement filtering by program, barangay, and criterion status:**
   - Support query params: `program_id`, `barangay_id`, `readiness_group`, `application_status`, `overall_eligibility`, `criterion_status`, `search`, and pagination.
5. **Implement applicant detail retrieval:**
   - `GET /api/v1/lgu/applicants/{application_id}/` returning full assessment snapshot, criterion breakdown, resident profile, document validation results, and barangay review notes/history.
6. **Display eligibility and document verification evidence:**
   - Ensure response includes exact observed vs. expected criterion values, fact provenance, OCR validation flags, and barangay escalation notes.
7. **Implement the LGU review interface:**
   - Web page `/lgu/reviews` and `/lgu/reviews/:id` with filter bar, readiness tabs, applicant detail view, and document viewer (`en`/`fil`/`hil`).
8. **Implement a barangay read-only review interface:**
   - Allow `BARANGAY_OFFICIAL` read-only access to forwarded/decided applicants **within their own barangay only** (`403`/`404` for any other barangay), hiding LGU selection/export actions.

## Sprint 05B — LGU Selection and Export (`sprint/05b-lgu-selection`)
**Dependencies:** `05A` | **Primary Targets:** `backend/apps/reviews/`, `web/src/`

1. **Implement selection decision records:**
   - `SelectionDecision` (`id` UUID, `application` FK, `decided_by` FK, `decision` [`SELECTED`/`NOT_SELECTED`], `justification`, `program_version` FK, `decided_at`) — immutable history table.
2. **Implement selection and non-selection services:**
   - `record_selection_decision(application, actor, decision, justification)` inside `transaction.atomic()` with `select_for_update()`, verifying actor has `IsLGUAdmin` / authorized `IsLGUPersonnel` in `application.lgu`.
3. **Implement decision justification requirements:**
   - Require non-empty `justification` (minimum character length) for both `SELECTED` and `NOT_SELECTED` decisions.
4. **Implement individual and bulk decision operations:**
   - `POST /api/v1/lgu/applications/{id}/decide/` and `POST /api/v1/lgu/applications/bulk-decide/` (validating all IDs belong to the caller's LGU and are in valid reviewable states atomically, returning clear per-item or transactional errors).
5. **Integrate selection decisions with application status transitions:**
   - Transition `Application.status` to `SELECTED` or `NOT_SELECTED` and append `ApplicationStatusHistory`.
6. **Implement the LGU application export functionality:**
   - `GET /api/v1/lgu/applications/export/?format=csv&...` streaming filtered LGU-scoped application/selection records as CSV (`text/csv`, `Content-Disposition: attachment`).
7. **Implement CSV export validation and sanitization:**
   - Neutralize CSV/Excel formula injection: prefix any cell value starting with `=`, `+`, `-`, `@`, `\t`, or `\r` with a leading single quote (`'`) before CSV serialization; never include raw secrets or storage keys.
8. **Implement export audit records:**
   - Record an `AuditEvent` (`lgu.applications.exported`) containing actor, LGU, filter params, and exported row count.
9. **Implement the LGU selection interface:**
   - Web controls on `/lgu/reviews` for individual/bulk Select & Not-Select modals (with justification input) and "Export CSV" button. Residents see their decision status in mobile/web application details.

## Sprint 05C — Distribution Tracking (`sprint/05c-distribution`)
**Dependencies:** `05B` | **Primary Targets:** `backend/apps/distributions/`, `web/src/`, `mobile/src/`

1. **Implement distribution records:**
   - `DistributionRecord` (`id` UUID, `application` OneToOne/FK, `lgu` FK, `barangay` FK, `program` FK, `status` [`SCHEDULED`/`RELEASED`/`UNCLAIMED`], `scheduled_date`, `released_at`, `released_by` FK nullable, `claimed_by_name`, `reference_code`, `notes`, timestamps) + `DistributionHistory` (audit/change trail).
2. **Implement distribution status management:**
   - Auto-create or allow scheduling `DistributionRecord` only for `SELECTED` applications; enforce valid transitions (`SCHEDULED` -> `RELEASED` or `UNCLAIMED`; block double release with `409 CONFLICT`).
3. **Implement barangay release recording:**
   - `POST /api/v1/distributions/{id}/release/` restricted to `IsBarangayOfficial` in the application's `barangay` (or authorized LGU personnel), updating `Application.status` to `DISTRIBUTED` inside `transaction.atomic()` and recording audit event.
4. **Implement unclaimed assistance recording:**
   - `POST /api/v1/distributions/{id}/mark-unclaimed/` with reason/notes, transitioning `Application.status` to `UNCLAIMED` and recording audit event.
5. **Implement distribution summary endpoints:**
   - `GET /api/v1/distributions/` (role/org-scoped) and `GET /api/v1/lgu/distributions/summary/` aggregating scheduled, released, and unclaimed counts by program and barangay.
6. **Implement the barangay distribution interface:**
   - Web page `/barangay/distributions` showing selected beneficiaries in the official's barangay with Release and Mark Unclaimed modal actions.
7. **Implement LGU distribution summaries:**
   - Web page `/lgu/distributions` displaying per-program and per-barangay distribution metrics and filterable ledger.
8. **Integrate distribution status into resident application timelines:**
   - Surface distribution schedule, release timestamp, and unclaimed status in `ApplicationDetailScreen` (mobile) and application status API.

## Sprint 05D — Messaging and Notifications (`sprint/05d-messaging`)
**Dependencies:** `04E` | **Primary Targets:** `backend/apps/notifications/`, `web/src/`, `mobile/src/`

1. **Implement conversation models:**
   - `Conversation` (`id` UUID, `application` FK, `resident` FK, `lgu` FK, `barangay` FK, `subject`, `last_message_at`, `created_at`).
2. **Implement message models:**
   - `Message` (`id` UUID, `conversation` FK, `sender` FK, `sender_role`, `body`, `created_at`) and `ConversationReadState` (`conversation` FK, `user` FK, `last_read_at`) for efficient per-user unread counts.
3. **Implement notification records:**
   - `Notification` (`id` UUID, `recipient` FK, `notification_type`, `title`, `body`, `target_type`, `target_id`, `is_read`, `read_at`, `created_at`).
4. **Establish conversation participation permissions:**
   - Only the application's owning `resident`, assigned `BARANGAY_OFFICIAL`s for that `barangay`, and authorized `LGU_PERSONNEL` for that `lgu` can view or post in the conversation. Deny cross-barangay, cross-LGU, and other-resident access (`403`/`404`).
5. **Implement message sending and retrieval:**
   - `GET /api/v1/conversations/`, `POST /api/v1/conversations/`, `GET /api/v1/conversations/{id}/messages/`, `POST /api/v1/conversations/{id}/messages/` with sanitized plain-text bodies (bounded length, no raw HTML rendering).
6. **Implement unread message tracking:**
   - `POST /api/v1/conversations/{id}/read/` updating `ConversationReadState.last_read_at` and returning `unread_count` on conversation list/summary endpoints.
7. **Implement notification retrieval and read status:**
   - `GET /api/v1/notifications/`, `POST /api/v1/notifications/{id}/read/`, `POST /api/v1/notifications/read-all/` returning unread count and paginated notifications for `request.user`.
8. **Trigger notifications for important application events:**
   - Emit in-app `Notification` records (via `notifications.services` called after commit or inside service hooks) on: resident approval/rejection, OCR completion/failure, document review/return/escalation, LGU selection decision, distribution release, and new message.
9. **Implement web messaging interfaces:**
   - Web inbox/thread view inside application/review detail and notification bell dropdown (`en`/`fil`/`hil`).
10. **Implement mobile messaging interfaces:**
    - Mobile `MessagesScreen`, `ConversationThreadScreen`, and `NotificationsScreen` (`en`/`fil`/`hil`).
11. **Implement foreground polling for new messages and notifications:**
    - Poll unread counts / active thread at a conservative interval (e.g., 15–30s) only while screen/app is foregrounded (`AppState` on mobile, `document.visibilityState` on web), cleaning up timers on unmount/background.

## Sprint 05E — Security Hardening (`sprint/05e-security-hardening`)
**Dependencies:** All feature sprints (`02A`–`05D`) | **Primary Targets:** `backend/`, `ai-service/`, `web/`, `mobile/`, `docs/security/`

1. **Conduct a system threat assessment:**
   - Review data flows (`web`/`mobile` -> `backend` -> `PostgreSQL`/`Redis`/`S3`/`ai-service`), document trust boundaries, and log findings in `docs/security/THREAT_MODEL.md`.
2. **Review authentication and authorization:**
   - Verify every endpoint in `backend/config/urls.py` and app `urls.py` has explicit `permission_classes` (defaulting to `IsAuthenticated`), JWT lifetimes/blacklisting, and password lockout.
3. **Review barangay and LGU data isolation:**
   - Audit every queryset in `residents`, `programs`, `eligibility`, `documents`, `applications`, `reviews`, `distributions`, `notifications`, and `audit` for missing org filters.
4. **Conduct IDOR and access control testing:**
   - Add systematic cross-resident, cross-barangay, cross-LGU, and role-escalation tests across every resource ID endpoint.
5. **Review document upload and storage security:**
   - Verify magic-byte verification, size caps, EXIF stripping, private S3 ACLs, short-lived presigned URLs, and safe `Content-Disposition: attachment` / `X-Content-Type-Options: nosniff` headers.
6. **Review sensitive information handling:**
   - Verify OCR text encryption at rest, PII redaction before AI extraction calls, audit metadata sanitization, and absence of PII/secrets in JSON logs.
7. **Review API security and input validation:**
   - Check pagination max limits, query parameter bounds, serializer `extra` / field allowlists, and protection against SQL injection / CSV formula injection / XSS.
8. **Review environment secrets and service authentication:**
   - Verify production startup fails fast if `DJANGO_SECRET_KEY`, `AI_SERVICE_API_KEY`, or `DOCUMENT_TEXT_ENCRYPTION_KEY` are missing/default when `DEBUG=False` / production.
9. **Configure security headers and CORS restrictions:**
   - Harden Django `SECURE_*` settings when `not DEBUG` (`SECURE_CONTENT_TYPE_NOSNIFF=True`, `X_FRAME_OPTIONS="DENY"`, `SECURE_SSL_REDIRECT`, HSTS, strict `CORS_ALLOWED_ORIGINS`, CSRF cookie flags for web cookie auth).
10. **Review dependency vulnerabilities:**
    - Run `pip-audit` / `safety` on `backend` & `ai-service` and `npm audit` at workspace root; upgrade vulnerable packages.
11. **Implement additional security tests:**
    - Add automated security regression suite (`backend/tests/test_security_hardening.py`) verifying headers, CORS, IDOR, upload rejection, and production config guards.
12. **Address identified high-priority findings:**
    - Fix all critical/high findings and document residual accepted risks in `docs/security/SECURITY.md` / `THREAT_MODEL.md`.

## Sprint 05F — System Integration and Performance Testing (`sprint/05f-integration-perf-testing`)
**Dependencies:** `05E` | **Primary Targets:** `backend/tests/`, `ai-service/tests/`, `web/`, `mobile/`, `docs/testing/`

1. **Integrate the resident, barangay, and LGU workflows:**
   - Run full stack locally via Docker Compose (`db`, `redis`, `minio`, `ai`, `worker`, `web`) + Vite + Expo and verify cross-service wiring end-to-end.
2. **Implement complete end-to-end test scenarios:**
   - Write automated E2E backend integration tests covering: Resident Register -> Barangay Approve -> Matching + Eligibility Assessment -> Document Upload + OCR + Validation -> Gap Analysis -> Submit Application -> Barangay Review/Escalate -> LGU Review + Select + Export -> Barangay Release -> Resident Timeline & Notifications.
3. **Test web and mobile API integration:**
   - Verify `@qualifil/api-client`, web cookie auth flows, and mobile bearer token refresh flows against live Django endpoints.
4. **Test Django and FastAPI communication:**
   - Verify `X-Request-ID` propagation, `X-Internal-API-Key` auth, timeout budgets, and standardized error parsing between Django and FastAPI.
5. **Test Celery and Redis background processing:**
   - Verify async execution (with eager mode disabled in integration test profile) for OCR, program embedding sync, and matching tasks, including worker restart/retry behavior.
6. **Test PostgreSQL and pgvector operations:**
   - Verify HNSW/IVFFlat index usage (`EXPLAIN ANALYZE`), concurrent `select_for_update()` safety, and migration cleanly applying from scratch on `pgvector/pgvector:pg18`.
7. **Test document upload and OCR workflows:**
   - Verify image + multi-page PDF uploads, EXIF stripping, Tesseract `eng+fil` extraction, encryption at rest, and validation flagging.
8. **Test AI service failure and fallback behavior:**
   - Stop `ai-service` / inject timeouts/503s and confirm: program publishing still succeeds, matching degrades to category/keyword search, explanations degrade to templates, and action plans degrade to deterministic steps.
9. **Conduct performance testing:**
   - Benchmark API p95 latency and concurrent request throughput (e.g., `locust` or `k6` script in `scripts/perf/`) for program listing, assessment creation, matching, and review queues.
10. **Evaluate embedding and reranking performance:**
    - Measure latency, throughput, and RSS memory of `Qwen/Qwen3-Embedding-0.6B` and `Qwen/Qwen3-Reranker-0.6B` on CPU (and GPU if available) and document Recall@K / MRR results.
11. **Evaluate eligibility engine accuracy:**
    - Run the complete golden dataset + property-based test suite and record 100% deterministic pass rate in `docs/testing/`.
12. **Evaluate OCR extraction performance:**
    - Run synthetic OCR benchmark dataset and document character accuracy, field extraction precision/recall, and processing time per page.
13. **Validate system behavior under the expected server configurations:**
    - Test resource limits simulating 8 GB and 16 GB RAM server profiles (e.g., Docker Compose `mem_limit` for Django, Celery, PostgreSQL, Redis, and FastAPI AI service) and document recommended worker concurrency and model memory footprints.

## Sprint 05G — Deployment Preparation and Release (`sprint/05g-deployment-prep`)
**Dependencies:** `05F` | **Primary Targets:** `backend/`, `ai-service/`, `web/`, `mobile/`, `scripts/`, `docs/runbooks/`

1. **Finalize production and staging deployment configurations:**
   - Add production Dockerfiles (multi-stage builds, non-root users, static asset collection) and `deploy/docker-compose.prod.yml` (or staging/prod Compose + env templates) without committing secrets.
2. **Configure application process management:**
   - Use `gunicorn` (or `uvicorn` workers) for Django WSGI/ASGI, `uvicorn` for FastAPI `ai-service`, and supervised Celery worker processes with graceful shutdown signals (`SIGTERM`).
3. **Configure reverse proxy and HTTPS:**
   - Add Nginx or Caddy reverse-proxy config routing `/` to built `web/dist`, `/api/` and `/admin/` to Django, enforcing TLS/HTTPS, request size caps matching `MAX_UPLOAD_SIZE_MB`, and **blocking** any external route to `ai-service`, Postgres, Redis, or MinIO admin.
4. **Establish production database migration procedures:**
   - Document and script pre-deploy migration check (`migrate --plan`, `manage.py check --deploy`) and zero/low-downtime migration sequence.
5. **Implement database backup and restoration procedures:**
   - Add `scripts/backup_db.sh` (`pg_dump -Fc`) and `scripts/restore_db.sh` (`pg_restore`) + S3 object storage backup instructions in `docs/runbooks/DEPLOYMENT.md`.
6. **Establish container image build and release workflows:**
   - Add GitHub Actions workflow `.github/workflows/release.yml` (or extend CI) to build and verify production Docker images for `backend`, `ai-service`, and `web`.
7. **Implement deployment health checks:**
   - Wire container/orchestrator probes to `GET /api/v1/health/`, `GET /api/v1/health/ready/`, and AI service `GET /health/live`, `GET /health/ready`.
8. **Implement deployment smoke tests:**
   - Create `scripts/smoke_test.py` (or `.sh`) verifying health endpoints, login, seeded program listing, assessment preview, and internal AI status after deployment.
9. **Conduct a rollback test:**
   - Execute and document a staging rollback drill (reverting container image tags + handling backward-compatible DB state).
10. **Conduct a database restoration drill:**
    - Restore a staging backup into a fresh PostgreSQL + pgvector instance and verify row counts, vector searches, and encrypted OCR text readability.
11. **Prepare mobile testing builds:**
    - Configure `mobile/eas.json` (or `npx expo export` / Android APK preview profile) pointing `EXPO_PUBLIC_API_BASE_URL` to staging HTTPS API and document distribution instructions.
12. **Finalize deployment documentation:**
    - Write `docs/runbooks/DEPLOYMENT.md` covering server sizing (8 GB vs 16 GB findings from `05F`), env vars, TLS, backups, monitoring, and incident response.
13. **Conduct final release verification:**
    - Verify all [SPRINT.md](SPRINT.md) Section 4 release requirements, update [PROGRESS.md](PROGRESS.md) and [CHANGELOG.md](CHANGELOG.md), and tag `v0.5.0`.
