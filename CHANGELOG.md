# Changelog

All notable changes to QUALIFIL are documented in this file.

The format is based on Keep a Changelog. Version numbers follow Semantic Versioning where applicable.

## [Unreleased]

### Added
- Organizations and RBAC sprint (02B) for v0.2.0:
  - `organizations.LGU`, `organizations.Barangay`, and `organizations.OrganizationMembership` models with UUID primary keys, case-insensitive code/name constraints, and staff scope invariants.
  - Reusable DRF permission classes (`IsSystemAdmin`, `IsResident`, `IsBarangayOfficial`, `IsLGUPersonnel`, `IsLGUAdmin`, `HasOrganizationRole`, `require_organization_roles`) and `OrganizationScopedMixin` / `scope_queryset_for_user` for barangay and LGU isolation.
  - LGU, barangay, and staff membership endpoints under `/api/v1/organizations/` and active `memberships` payload on `GET /api/v1/auth/me/`.
  - Idempotent `seed_organizations` management command seeding City of Silay and 16 barangays.
  - Typed organization endpoints and membership DTOs in `@qualifil/api-client`.
  - Organization API contract in `docs/api/ORGANIZATIONS.md`.
- Authentication sprint (02A) for v0.2.0:
  - Custom UUID `accounts.User` with normalized email login, base roles, password-hash fields, failed-login counter, and lockout timestamp.
  - SimpleJWT access/refresh tokens with rotation and DB-backed blacklisting.
  - Registration, login, refresh, logout, `me`, change-password, and CSRF endpoints under `/api/v1/auth/`.
  - Bearer-token transport for mobile and httpOnly cookie transport with CSRF protection for web.
  - Typed `auth` helpers, cookie support, and single-shot 401 refresh-retry in `@qualifil/api-client`.
  - Secure refresh-token storage on mobile and cookie-backed web client configuration.
  - Authentication API contract in `docs/api/AUTHENTICATION.md`.
- Initial sprint and release planning structure.
- Initial repository documentation templates.
- QUALIFIL backend (Django + Django REST Framework) foundation for v0.1.0:
  - Modular Django settings for development and testing.
  - Django REST Framework configuration with the standardized error handler.
  - `/api/v1/` API namespace with liveness and readiness health endpoints.
  - PostgreSQL 18 + pgvector configuration with a pgvector extension system check.
  - Redis caching and Celery background-processing configuration.
  - Standardized API error responses and Django-level 404/500 handlers.
  - Structured request logging with JSON formatting and request IDs.
  - S3-compatible storage configuration for development.
  - Docker and Docker Compose services for the backend, database, Redis, and worker.
  - pytest/pytest-django setup with backend tests wired into CI.
- QUALIFIL AI service (FastAPI) foundation for v0.1.0:
  - Application factory with modular `api`, `core`, `schemas`, and provider/service packages.
  - Environment-based settings with validation and production key enforcement.
  - Internal service authentication using the `X-Internal-API-Key` header.
  - Public liveness and readiness endpoints.
  - Internal model-status endpoint reporting configured models as `not_loaded`.
  - Standardized error envelope shared with the Django backend.
  - Request-ID handling and structured request logging.
  - Docker image and Docker Compose service integration.
  - AI service pytest suite wired into CI.
  - Internal API contract documented in `docs/api/AI_SERVICE.md`.
- Shared foundation for v0.1.0:
  - `packages/api-client` npm workspace providing one typed HTTP client for web and mobile, including standardized error-envelope handling, bearer tokens, timeouts, and an injectable `fetch` for tests.
  - Root npm workspace configuration covering `packages/*`, `web`, and `mobile`.
  - Prettier, `.editorconfig`, and shared formatting scripts.
  - Local development runbook in `docs/runbooks/LOCAL_DEVELOPMENT.md`.
  - Dependency and credentials checklist in `docs/runbooks/DEPENDENCY_CHECKLIST.md`.
- QUALIFIL web application foundation for v0.1.0:
  - React 18, TypeScript, Vite 5, Tailwind CSS 3, and shadcn/ui style components.
  - Routing, English/Filipino/Hiligaynon localization, API client integration, and an application status page.
  - Vitest and Testing Library component, API, localization, and page tests.
- QUALIFIL mobile application foundation for v0.1.0:
  - Expo SDK 58, React Native 0.88, and TypeScript application scaffold.
  - React Navigation native stack with connectivity and settings screens.
  - English/Filipino/Hiligaynon localization with persisted locale selection.
  - Secure token storage abstraction using `expo-secure-store`, with a documented web fallback.
  - Mobile API layer built on `@qualifil/api-client`.
  - `jest-expo` and React Native Testing Library component, API, storage, localization, and screen tests.

### Changed
- DRF now defaults to JWT authentication and `IsAuthenticated`; health and auth endpoints opt out explicitly.
- Web API client now uses cookie credentials and the cookie auth transport; the mobile client uses bearer tokens from secure storage.
- Backend and AI service now load the repository-root `.env` with `python-dotenv`; real environment variables take precedence, so container and CI configuration is never overwritten.
- `VITE_API_BASE_URL` and `EXPO_PUBLIC_API_BASE_URL` are treated as API origins rather than `/api`-suffixed paths, and Vite reads the root `.env` via `envDir`.
- Added `django-cors-headers` with the configurable `DJANGO_CORS_ALLOWED_ORIGINS` allowlist while keeping the Vite development proxy.
- CI web and mobile jobs now install the npm workspace from the repository root and run the shared client checks.
- Replaced the parser-only web ESLint configuration with enforced TypeScript and React Hooks rules; the shared client and mobile app have equivalent setups.
- Web dependencies moved into the root npm workspace and the per-app lockfile was removed.

### Fixed
- Custom `api.errors` exception classes now define the DRF `status_code` attribute, so `Unauthorized`, `Forbidden`, and other API errors return their intended HTTP statuses instead of 500.
- An unreachable database during `manage.py check` now produces the `api.W001` warning instead of a hard error, and the database connectivity test skips instead of failing when PostgreSQL is not running locally.
- CI web and mobile jobs now fail instead of silently skipping when their manifests are missing.
- Root-level `pytest` now collects both the backend and AI service suites using a shared `pytest.ini` with the correct Django settings, import paths, and import mode.

### Security
- Secrets and credentials are read from environment variables so they stay out of version control.
- Failed logins are throttled and lock the account after repeated attempts; lockout responses use `429 TOO_MANY_REQUESTS` and invalid credentials never reveal whether an email exists.
- Refresh tokens are revoked on rotation, logout, and password change; web cookie requests require a CSRF token and web JWTs are never stored in `localStorage`.

## [0.1.0] — Not Released

### Added
- Project repository foundation.
- Backend project foundation.
- Dedicated AI service foundation.
- Web application foundation.
- Mobile application foundation.
- Initial automated CI workflow.

## [0.2.0] — Not Released

### Added
- Authentication and token management.
- Organization and role-based access control.
- Audit logging.
- Resident registration and profile management.
- Assistance program management.
- Initial web and mobile authentication interfaces.

## [0.3.0] — Not Released

### Added
- Program knowledge base and seed import.
- Deterministic eligibility assessment engine.
- Immutable assessment snapshots.
- AI embedding and reranking integration.
- Program matching pipeline.
- Eligibility explanations.

## [0.4.0] — Not Released

### Added
- Document upload and storage.
- OCR processing.
- Document completeness and consistency validation.
- Requirement gap analysis.
- Application submission and status tracking.
- Barangay review and escalation workflows.

## [0.5.0] — Not Released

### Added
- LGU applicant review workflow.
- Applicant selection and export capabilities.
- Assistance distribution tracking.
- Notifications and messaging, subject to confirmed scope.
- Security hardening.
- System integration and performance validation.
- Deployment preparation.

---

## Change Entry Guidelines

Use the following categories:

- **Added** — New functionality.
- **Changed** — Changes to existing functionality.
- **Deprecated** — Functionality scheduled for removal.
- **Removed** — Removed functionality.
- **Fixed** — Bug fixes.
- **Security** — Security-related changes.

Do not record every minor code edit. Record user-visible functionality, API changes, database or migration changes, security changes, and other meaningful project changes.