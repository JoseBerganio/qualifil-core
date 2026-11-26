# AGENTS.md — AI Coding Agent Instructions for QUALIFIL

This file is the authoritative operational guide for AI coding agents working in `qualifil-core`. Follow every rule below before planning, editing, or reviewing code.

---

## 1. Project Identity & Current State

**QUALIFIL** is a cross-platform Local Government Assistance Information and Application Management System (thesis project targeting Silay City / Philippine LGU and barangay workflows).

- **Current Milestone State** (verify in [PROGRESS.md](PROGRESS.md) and [SPRINT.md](SPRINT.md)):
  - **v0.1.0 (Project Foundation)** — Sprints `01A`–`01E` are implemented (`backend/`, `ai-service/`, `packages/api-client/`, `web/`, `mobile/`, CI).
  - **v0.2.0 – v0.5.0** — Planned in [SPRINT.md](SPRINT.md). Refer to [IMPLEMENTATION.md](IMPLEMENTATION.md) for task-by-task implementation guidance.
- **Primary Reference Documents**:
  - [SPRINT.md](SPRINT.md) — Sprint scope, dependencies, implementation tasks, tests, and acceptance criteria.
  - [IMPLEMENTATION.md](IMPLEMENTATION.md) — Detailed engineering playbook for every sprint task across `v0.1.0`–`v0.5.0`.
  - [docs/architecture/OVERVIEW.md](docs/architecture/OVERVIEW.md) — System architecture, data ownership, flows, and constraints.
  - [docs/architecture/MODULES.md](docs/architecture/MODULES.md) — Django app boundaries and dependency rules.
  - [docs/adr/0001-modular-monolith-and-ai-service.md](docs/adr/0001-modular-monolith-and-ai-service.md) — Modular monolith + dedicated AI service ADR.
  - [docs/api/AI_SERVICE.md](docs/api/AI_SERVICE.md) — Internal FastAPI contract.
  - [docs/security/SECURITY.md](docs/security/SECURITY.md) — Baseline security controls.
  - [docs/testing/TEST_STRATEGY.md](docs/testing/TEST_STRATEGY.md) — Testing standards and domain invariants.
  - [docs/runbooks/LOCAL_DEVELOPMENT.md](docs/runbooks/LOCAL_DEVELOPMENT.md) — Local environment setup.

---

## 2. Repository Map

```text
qualifil-core/
├── backend/                 # Django 5.x + DRF modular monolith (authoritative backend)
│   ├── api/                 # Shared API utilities: errors.py, logging.py, checks.py, tasks.py, views/
│   ├── apps/                # 11 domain Django apps (currently scaffolded __init__.py)
│   │   ├── accounts/        # Identity, custom user, auth, JWT
│   │   ├── organizations/   # LGU, Barangay, staff memberships, RBAC permissions
│   │   ├── audit/           # Immutable audit log events & sanitizer
│   │   ├── residents/       # Resident profiles, consent, barangay approval, fact provenance
│   │   ├── programs/        # Categories, programs, immutable versions, criteria, requirements, embeddings
│   │   ├── eligibility/     # Pure deterministic engine, assessment snapshots, matching, explanations
│   │   ├── documents/       # Upload, S3 storage, OCR tasks/records, validation rules, gap analysis
│   │   ├── applications/    # Application lifecycle, attachments, status history
│   │   ├── reviews/         # Barangay document review, LGU review list, escalation, selection, export
│   │   ├── distributions/   # Release & unclaimed tracking, summaries
│   │   └── notifications/   # Conversations, messages, notifications
│   ├── config/              # settings/{base,development,testing}.py, urls.py, celery.py, wsgi.py, asgi.py
│   ├── docker/              # init.sql (pgvector extension)
│   ├── requirements/        # base.txt, dev.txt
│   └── tests/               # Backend pytest suite
├── ai-service/              # Dedicated FastAPI AI microservice (derived outputs only)
│   ├── app/
│   │   ├── api/             # dependencies.py, errors.py, middleware.py, routes/{health,models}.py
│   │   ├── core/            # config.py (Settings), logging.py
│   │   ├── schemas/         # common.py (ServiceRequest/ServiceResponse/ErrorResponse), health.py, models.py
│   │   └── services/        # model_registry.py, providers/base.py
│   └── tests/               # AI service pytest suite
├── packages/
│   └── api-client/          # Shared TypeScript HTTP client (@qualifil/api-client) for web & mobile
├── web/                     # React 18 + Vite 5 + TS + Tailwind + shadcn/ui style web app
├── mobile/                  # Expo SDK 58 + React Native 0.88 + TS + React Navigation v7 mobile app
├── docs/                    # Architecture, ADRs, API contracts, runbooks, security, testing
├── .github/workflows/ci.yml # CI pipelines: backend-tests, ai-service-tests, web-checks, mobile-checks
├── .env.example             # Single shared environment template at repo root
├── package.json             # Root npm workspace (packages/*, web, mobile) + Prettier scripts
└── pytest.ini               # Root pytest config running backend/tests and ai-service/tests
```

> **Note:** `README.md` sketches `ai-service/app/models/`, whereas the implemented Sprint `01C` layout uses `ai-service/app/schemas/` and `ai-service/app/services/providers/`. Always follow the actual implemented structure in `ai-service/app/`.

---

## 3. Non-Negotiable Architectural & Domain Invariants

Violating any rule below is a blocking defect:

1. **Django Owns Authoritative Data & Business Rules**
   - PostgreSQL (via Django ORM) is the single system of record.
   - `ai-service` **must never** connect to PostgreSQL, directly mutate business records, approve/reject residents, alter eligibility results, or select applicants.
   - Web and mobile clients **must never** call `ai-service`, PostgreSQL, Redis, or S3 directly. All client traffic goes through Django `/api/v1/...`.

2. **Deterministic Eligibility Engine (`Met` / `Unmet` / `Unknown`)**
   - Eligibility evaluation must live in a **pure Python domain module** independent of Django ORM models and AI calls so it can be unit-tested in isolation.
   - Every criterion resolves to exactly one of three states: `Met`, `Unmet`, or `Unknown`.
   - **`Unknown` must NEVER be silently converted to `Unmet`.** Missing or unverified facts produce `Unknown`.
   - Assessments indicate *potential eligibility*, never guaranteed approval.
   - Every persisted assessment must be an **immutable snapshot** capturing: resident fact snapshot, published program version, rule/engine version, per-criterion outcomes, and overall outcome. Editing a program or resident profile must never mutate past assessments.

3. **AI-Assisted Features Are Non-Authoritative & Degrade Gracefully**
   - Semantic matching (embeddings + reranking) is retrieval support, not proof of eligibility.
   - LLM explanations and action plans must be grounded in deterministic outputs, validated against schemas, checked against prohibited approval/guarantee language, and backed by deterministic templates when `ai-service` or Anthropic is unavailable.
   - AI/embedding failures must never block saving, publishing, or submitting authoritative Django records.

4. **Document Processing & OCR Boundaries**
   - Automated OCR and validation check completeness, readability, expiration, and cross-field consistency **only**. They do **not** verify legal/physical document authenticity.
   - OCR output is never automatically treated as verified truth; human review (`reviews`) handles verification and escalation.
   - Uploaded documents are private in S3-compatible storage; never expose permanent public URLs or storage credentials to clients.

5. **Strict Server-Side Authorization & Org Isolation**
   - Never rely on frontend UI hiding for security. Enforce role and organization scoping on every Django view/queryset.
   - Barangay officials only access residents, documents, applications, and distributions within their assigned barangay.
   - LGU personnel/admins only access programs, applications, selections, and audit logs within their assigned LGU.
   - Always test both **allowed** and **denied** paths (401, 403, cross-barangay, cross-LGU, IDOR).

6. **Thesis Scope Boundaries**
   - Do **not** implement external DSWD/government API integrations, external national ID verification, payment processing, or automated applicant ranking/scoring weights without an explicit approved ADR/decision.

---

## 4. Coding Conventions by Layer

### 4.1 Environment Configuration
- The repository uses **one shared `.env`** at the repo root (`.env.example`).
- `backend/config/settings/base.py` and `ai-service/app/core/config.py` load `../.env` with `python-dotenv` using `override=False` so real environment variables (Docker/CI) take precedence.
- Vite reads the root `.env` via `envDir: ".."`.
- **Never** commit `.env` or hardcode secrets. **Never** put secrets in `VITE_*` or `EXPO_PUBLIC_*` variables.
- Any new environment variable added in code must be documented in `.env.example` and relevant docs.

### 4.2 Django Backend (`backend/`)
- **Apps & Boundaries**: Place domain models, services, serializers, permissions, and views inside the appropriate `backend/apps/<app>/` directory (`INSTALLED_APPS` already lists all 11 apps in `backend/config/settings/base.py`).
  - Keep views/viewsets thin and serializers focused on input/output schema validation.
  - Put business rules and multi-step orchestration in `services.py` (or a `services/` package) wrapped in `django.db.transaction.atomic()` when mutating multiple records.
  - Avoid circular imports between `apps.*`. Use documented service interfaces rather than mutating another app's models directly.
  - Keep `audit` decoupled: domain services emit audit events through a centralized `apps.audit.services` function.
- **URL Namespace**: Mount all new API routes under `/api/v1/` in `backend/config/urls.py` (delegating to `apps.<app>.urls`).
- **Standardized Error Envelope**: Do not invent custom error JSON shapes. Use `rest_framework.exceptions` or subclasses of `api.errors.APIError` (`BadRequest`, `Unauthorized`, `Forbidden`, `NotFound`, `Conflict`) so `api.errors.exception_handler` returns:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable summary.",
      "status": 400,
      "details": [{ "field": "name", "message": "Field error." }]
    }
  }
  ```
- **Logging**: Use Python `logging.getLogger(__name__)`. Logs are formatted as JSON by `api.logging.JSONFormatter` and correlated via `X-Request-ID`. **Never** log passwords, tokens, API keys, OCR raw text, or sensitive resident PII.
- **Migrations**: Every model change requires an explicit Django migration (`python backend/manage.py makemigrations`) checked into git and tested.
- **Celery Tasks**: Define tasks in `apps.<app>/tasks.py` using `from config.celery import app` (or `@shared_task`), make them idempotent, configure bounded retries, and handle `CELERY_TASK_ALWAYS_EAGER=True` in `testing.py`.

### 4.3 FastAPI AI Service (`ai-service/`)
- **App Factory**: Register routers, middleware, and dependencies in `ai-service/app/main.py` (`create_app`).
- **Internal Auth**: Every `/internal/v1/...` route MUST depend on `require_internal_api_key` (`X-Internal-API-Key` validated with `hmac.compare_digest`). Only `/health/live` and `/health/ready` are public.
- **Strict Schemas**: Inherit request models from `app.schemas.common.ServiceRequest` (`extra="forbid"`, `str_strip_whitespace=True`) and response models from `ServiceResponse` (`extra="forbid"`).
- **Error Envelope**: Raise `app.api.errors.ServiceError` so errors match the Django `{ "error": { "code", "message", "status", "details" } }` contract.
- **Provider Abstraction**: Implement model backends behind `EmbeddingProvider`, `RerankProvider`, and `ExplanationProvider` in `app/services/providers/`. Always provide a **deterministic fake/stub provider** for unit/CI tests; never require live Anthropic calls, GPU, or HuggingFace model downloads in default `pytest`.
- **Contract Docs**: Update [docs/api/AI_SERVICE.md](docs/api/AI_SERVICE.md) whenever adding or modifying internal AI endpoints.

### 4.4 Shared API Client (`packages/api-client/`)
- Every endpoint DTO and client helper shared by web and mobile should be added to `@qualifil/api-client` (`packages/api-client/src/`).
- After editing `packages/api-client`, **always rebuild** it (`npm run build -w @qualifil/api-client`) so `packages/api-client/dist/` is up to date for `web/` and `mobile/` TypeScript/Metro builds.
- Preserve `ApiError`, `createApiClient`, and injectable `fetchImpl` for unit testing.

### 4.5 Web (`web/`) & Mobile (`mobile/`)
- **No Business Logic in UI**: Never implement eligibility calculations, permission decisions, or rule evaluation in React/React Native components.
- **API Access**: Web uses `web/src/lib/api/` backed by `@qualifil/api-client` (with empty `VITE_API_BASE_URL` in dev to use Vite's `/api` proxy). Mobile uses `mobile/src/lib/api/` backed by `@qualifil/api-client` + `tokenStorage`.
- **Auth Token Handling**:
  - Mobile native uses `expo-secure-store` via `mobile/src/lib/storage/tokenStorage.ts`.
  - Web uses the httpOnly-cookie / CSRF or memory-token flow established in Sprint `02A`/`02F` (do **not** store JWTs in `localStorage`).
- **Localization (`en`, `fil`, `hil`)**: Every user-visible string in `web/` and `mobile/` must have translation keys in all three locale files:
  - Web: `web/src/lib/i18n/locales/{en,fil,hil}.json`
  - Mobile: `mobile/src/lib/i18n/locales/{en,fil,hil}.json`
- **Formatting**: Match `.editorconfig` and `.prettierrc` (`"semi": true`, `"singleQuote": false`, `"trailingComma": "all"`, `"printWidth": 100`; LF line endings; 2 spaces for TS/JS/JSON/MD, 4 spaces for Python).

---

## 5. Git, Sprint & Documentation Workflow

1. **Branching**: Create a branch per sprint from the latest approved `main` using `sprint/NNx-short-description` (see [SPRINT.md](SPRINT.md)).
2. **Scope Discipline**: Implement only the tasks and dependencies belonging to the active sprint. Do not start a sprint before its dependencies in [SPRINT.md](SPRINT.md) are satisfied.
3. **Update Project Docs**: When completing a sprint or meaningful change:
   - Update [PROGRESS.md](PROGRESS.md) (checkboxes, Active Work, Completed Work Log).
   - Update [CHANGELOG.md](CHANGELOG.md) under `## [Unreleased]` using Keep a Changelog categories (`Added`, `Changed`, `Fixed`, `Security`).
   - Update `docs/api/` or `docs/adr/` if API contracts or architectural decisions changed.

---

## 6. Verification Commands (Must Pass Before Completing Work)

Run from the repository root (unless noted):

```sh
# 1. Python tests (both backend and ai-service via root pytest.ini)
python -m pytest

# Or run individually:
python -m pytest backend
python -m pytest ai-service

# Backend Django system checks & migration drift check
python backend/manage.py check
python backend/manage.py makemigrations --check --dry-run

# 2. Shared API client (must build before web/mobile checks)
npm run build -w @qualifil/api-client
npm run lint -w @qualifil/api-client
npm test -w @qualifil/api-client

# 3. Web checks
npm run build -w qualifil-web
npm run lint -w qualifil-web
npm test -w qualifil-web -- --run

# 4. Mobile checks
npm run lint -w qualifil-mobile
npm run typecheck -w qualifil-mobile
npm test -w qualifil-mobile -- --watchAll=false --runInBand

# 5. Formatting check
npm run format:check
```

### Testing Guardrails
- **Synthetic Data Only**: Never put real names, addresses, phone numbers, government IDs, or real resident documents in tests, fixtures, or seed files.
- **No Live Paid APIs in CI**: Mock or use deterministic doubles for Anthropic, HuggingFace model weights, S3 (unless testing against MinIO/mock), and Tesseract where appropriate in unit tests; keep heavy model integration tests gated behind explicit markers/manual commands.
- **Test Both Paths**: Every new endpoint/service must test valid inputs, validation errors (400/422), unauthenticated access (401), unauthorized role/org access (403), and cross-organization isolation.
