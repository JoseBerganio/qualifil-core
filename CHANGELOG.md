# Changelog

All notable changes to QUALIFIL are documented in this file.

The format is based on Keep a Changelog. Version numbers follow Semantic Versioning where applicable.

## [Unreleased]

### Added
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

### Changed
- Nothing yet.

### Fixed
- Nothing yet.

### Security
- Secrets and credentials are read from environment variables so they stay out of version control.

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