# QUALIFIL — Development Progress

## Project Information

- Project: QUALIFIL
- Current target release: v0.1.0
- Current sprint: 01E — Mobile Foundation
- Overall status: In Progress
- Last updated: 2026-11-26

## Status Definitions

- **Planned** — Work has not started.
- **In Progress** — Implementation is underway.
- **Blocked** — Work cannot continue because of an unresolved dependency or issue.
- **Review** — Implementation is complete and awaiting review or validation.
- **Completed** — Acceptance criteria have been met and changes have been merged.

## Release Progress

### v0.1.0 — Project Foundation

Status: In Progress

- [x] 01A — Project Structure and CI Foundation
- [x] 01B — Backend Foundation
- [x] 01C — AI Service Foundation
- [x] 01D — Web Foundation
- [x] 01E — Mobile Foundation

### v0.2.0 — Authentication and Core Data

Status: Planned

- [ ] 02A — Authentication
- [ ] 02B — Organizations and Role-Based Access Control
- [ ] 02C — Audit Logging
- [ ] 02D — Resident Registration and Profile
- [ ] 02E — Assistance Program Management
- [ ] 02F — Web Authentication and Program UI
- [ ] 02G — Mobile Authentication and Profile UI

### v0.3.0 — Eligibility and Program Matching

Status: Planned

- [ ] 03A — Knowledge Base and Program Seeding
- [ ] 03B — Deterministic Eligibility Engine
- [ ] 03C — Assessment Snapshots and API
- [ ] 03D — AI Embedding and Reranking Service
- [ ] 03E — Program Embedding Synchronization
- [ ] 03F — Program Matching Pipeline
- [ ] 03G — Eligibility Explanations
- [ ] 03H — Mobile Matching UI and LGU Rule Preview

### v0.4.0 — Documents and Applications

Status: Planned

- [ ] 04A — Document Storage and Upload
- [ ] 04B — OCR Processing
- [ ] 04C — Document Validation
- [ ] 04D — Requirement Gap Analysis and Action Plans
- [ ] 04E — Application Submission and Status
- [ ] 04F — Barangay Document Review and Escalation
- [ ] 04G — Mobile Document and Application UI

### v0.5.0 — LGU Review and System Integration

Status: Planned

- [ ] 05A — Applicant Review List
- [ ] 05B — LGU Selection and Export
- [ ] 05C — Distribution Tracking
- [ ] 05D — Messaging and Notifications
- [ ] 05E — Security Hardening
- [ ] 05F — System Integration and Performance Testing
- [ ] 05G — Deployment Preparation and Release

## Active Work

### Sprint 01C — AI Service Foundation

Branch: `sprint/01c-ai-service-foundation`

Implemented:

- FastAPI application with an application factory for testability.
- Modular `api`, `core`, `schemas`, and `services/providers` package layout.
- Environment-based settings with validation and production key enforcement.
- Internal authentication through the `X-Internal-API-Key` header.
- Public liveness and readiness endpoints.
- Internal model-status endpoint reporting configured models as `not_loaded`.
- Standardized error envelope matching the Django backend.
- Request-ID handling, structured request logging, and standardized 500 responses.
- Docker image and Docker Compose service integration.
- AI service test suite wired into CI.
- Internal API contract documented in `docs/api/AI_SERVICE.md`.

Model loading and inference remain deferred to v0.3.0 as specified by the sprint plan.

### Sprint 01D — Web Foundation

Branch: `sprint/01d-web-foundation`

Implemented:

- React 18 + Vite 5 + TypeScript web application scaffold (`web/`).
- Tailwind CSS 3 with the HSL token theme and shadcn/ui style `Button` component.
- Routing with `react-router-dom` (`/` and `/status`).
- Context-based localization (`I18nProvider`, `useTranslation`) with locale switch persistence in localStorage.
- Fetch-based API client (`apiGet`, `apiPost`) for the Django backend; `getAppStatus()` calls `GET /api/v1/health/`.
- Initial application status page rendering environment and version with a localized error state.
- Component, API client, status, i18n, and page tests wired into CI; `web` and `mobile` CI jobs now fail instead of skipping when their manifests are missing.

### Sprint 01E — Mobile Foundation

Branch: `sprint/01e-mobile-foundation`

Implemented:

- Expo SDK 58 + React Native 0.88 + TypeScript application scaffold (`mobile/`).
- React Navigation native stack with a backend connectivity screen and a settings screen.
- English, Filipino, and Hiligaynon localization via an AsyncStorage-backed provider and language switcher.
- Secure token storage abstraction using `expo-secure-store` on native platforms and an explicitly documented in-memory fallback on web.
- Mobile API layer built on the shared `@qualifil/api-client` package.
- Component, API, storage, localization, and screen tests using `jest-expo` and React Native Testing Library.
- Reusable theme tokens and `Screen`, `Button`, `StatusCard`, and `LanguageSwitcher` components.
- Mobile lint, typecheck, and test checks wired into CI through the npm workspace.

### Cross-Cutting Foundation Fixes

Implemented before Sprint 01E:

- Added `packages/api-client` as a shared npm workspace consumed by web and mobile.
- Added real `.env` loading (`python-dotenv`) for the Django and FastAPI services, with real environment variables taking precedence.
- Normalized API base URLs so `VITE_API_BASE_URL` and `EXPO_PUBLIC_API_BASE_URL` are origins, not `/api`-suffixed paths; Vite now reads the root `.env` via `envDir`.
- Added `django-cors-headers` with a configurable `DJANGO_CORS_ALLOWED_ORIGINS` allowlist alongside the Vite dev proxy.
- Downgraded an unreachable database during `manage.py check` from an error to the `api.W001` warning, and made the database connectivity test skip when PostgreSQL is unavailable.
- Replaced the no-op web ESLint configuration with real TypeScript and React Hooks rules; added matching lint setups for the shared client and mobile app.
- Added Prettier, `.editorconfig`, and formatting scripts.
- Reworked CI to install the npm workspace from the repository root and run shared client, web, and mobile checks.

## Blockers and Risks

| Date | Sprint | Blocker or Risk | Owner | Resolution | Status |
|---|---|---|---|---|---|
| 2026-11-24 | 01C | No blockers recorded | — | — | — |

## Completed Work Log

| Date | Sprint | Summary | Pull Request / Commit |
|---|---|---|---|
| 2026-11-24 | 01B | Django backend foundation with PostgreSQL, pgvector, Redis, Celery, storage, structured errors/logging, Docker, and CI tests. | `sprint/01b-backend-foundation` |
| 2026-11-24 | 01C | FastAPI AI service foundation with internal authentication, health and model-status endpoints, standardized schemas/errors, Docker integration, and CI tests. | `sprint/01c-ai-service-foundation` |
| 2026-11-24 | 01D | React web application foundation with Vite, TypeScript, Tailwind, shadcn/ui style components, routing, localization, Django API client, initial application status page, and CI web checks. | `sprint/01d-web-foundation` |
| 2026-11-26 | 01E | Expo mobile application foundation with navigation, localization, secure token storage, shared API client integration, backend connectivity screen, and mobile CI checks. Also introduced the shared `@qualifil/api-client` workspace and fixed environment, CORS, lint, and CI foundations. | `sprint/01e-mobile-foundation` |

## Change Log for This File

Record meaningful progress updates here. Detailed version changes belong in `CHANGELOG.md`.

- YYYY-MM-DD — Initial progress tracker created.
- 2026-11-24 — Recorded Sprint 01B completion and Sprint 01C AI service foundation.
- 2026-11-24 — Recorded Sprint 01D web foundation completion.
- 2026-11-26 — Recorded Sprint 01E mobile foundation completion and cross-cutting foundation fixes.
