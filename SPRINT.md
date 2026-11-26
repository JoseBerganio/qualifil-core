# QUALIFIL — Sprint Development Plan

**Project:** QUALIFIL  
**Target Releases:** v0.1.0 – v0.5.0  
**Document Status:** Planning  
**Sprint Statuses:** Planned, In Progress, Blocked, Completed

---

# 1. Development Roadmap

## v0.1.0 — Project Foundation

Establish the repository, development environment, backend, AI service, web application, mobile application, and initial automated testing infrastructure.

Sprints:
- 01A — Project Structure and CI Foundation
- 01B — Backend Foundation
- 01C — AI Service Foundation
- 01D — Web Application Foundation
- 01E — Mobile Application Foundation

## v0.2.0 — Authentication and Core Data Management

Implement user authentication, role-based authorization, organization management, resident profiles, and assistance program management.

Sprints:
- 02A — Authentication
- 02B — Organizations and Role-Based Access Control
- 02C — Audit Logging
- 02D — Resident Registration and Profiles
- 02E — Assistance Program Management
- 02F — Web Authentication and Program Management UI
- 02G — Mobile Authentication and Resident Profile UI

## v0.3.0 — Eligibility Assessment and Program Matching

Implement the deterministic eligibility engine, assessment snapshots, knowledge base, embeddings, program matching, reranking, and AI-assisted explanations.

Sprints:
- 03A — Knowledge Base and Program Seeding
- 03B — Eligibility Engine
- 03C — Assessment Snapshots and API
- 03D — AI Embedding and Reranking Service
- 03E — Program Embedding Synchronization
- 03F — Program Matching Pipeline
- 03G — Eligibility Explanations
- 03H — Mobile Matching UI and LGU Rule Preview

## v0.4.0 — Document Processing and Application Management

Implement document uploads, OCR, document validation, requirement gap analysis, application submission, and barangay-level document review.

Sprints:
- 04A — Document Storage and Upload
- 04B — OCR Processing
- 04C — Document Validation
- 04D — Requirement Gap Analysis and Action Plans
- 04E — Application Submission and Status Tracking
- 04F — Barangay Document Review and Escalation
- 04G — Mobile Document and Application UI

## v0.5.0 — LGU Review and System Integration

Implement LGU applicant review, final selection, distribution tracking, messaging, security hardening, integration testing, and deployment preparation.

Sprints:
- 05A — Applicant Review List
- 05B — LGU Selection and Export
- 05C — Distribution Tracking
- 05D — Messaging and Notifications
- 05E — Security Hardening
- 05F — System Integration and Performance Testing
- 05G — Deployment Preparation and Release

---

# 2. Sprint Development Standards

## 2.1 Sprint Branching

Every sprint and sprint subdivision must have its own GitHub branch.

Use the following naming convention:

` sprint/NNx-short-description `

Examples:

- `sprint/01a-project-structure`
- `sprint/01b-backend-foundation`
- `sprint/02a-authentication`
- `sprint/03b-eligibility-engine`

Each sprint branch must be created from the latest approved `main` branch.

Completed sprint branches must be merged through pull requests. Use squash merging unless a project-level decision changes this convention.

## 2.2 Sprint Structure

Every sprint must contain the following information:

### Sprint Identification
- Sprint number and title.
- Target release.
- GitHub branch.
- Objective.
- Estimated duration.
- Dependencies.

### Scope
Describe the modules, features, and application components affected by the sprint.

### Implementation Tasks
List the specific development tasks, including:
- Backend implementation.
- Web implementation.
- Mobile implementation.
- AI service implementation, when applicable.
- Database and API changes.
- Integration requirements.

### Testing
Identify the required:
- Unit tests.
- Integration tests.
- API tests.
- Authorization tests.
- Frontend and mobile tests.
- Regression tests.

### Acceptance Criteria
Define observable conditions that must be satisfied before the sprint is considered complete.

## 2.3 Global Definition of Done

A sprint is considered complete only when:

- All approved sprint tasks are implemented.
- Required automated tests are written and passing.
- Relevant integration tests pass.
- No known critical regression is introduced.
- Database migrations are included and validated when necessary.
- API contracts are updated when affected.
- CI checks pass.
- Changes have been reviewed and approved.
- The sprint branch has been merged into `main`.
- Sprint progress and significant changes have been recorded in their respective project documentation.

---

# 3. Detailed Sprint Plans

# v0.1.0 — Project Foundation

## Sprint 01A — Project Structure and CI Foundation

**Branch:** `sprint/01a-project-structure`  
**Duration:** 3 working days  
**Dependencies:** None

### Objective
Establish the initial GitHub repository structure, development conventions, and automated CI foundation.

### Implementation Tasks

1. Initialize the QUALIFIL repository.
2. Establish the initial monorepo directory structure.
3. Create the initial project documentation files.
4. Configure GitHub Actions with an initial CI workflow.
5. Establish pull request and branch protection requirements.
6. Configure basic repository hygiene checks.
7. Establish initial code formatting and linting conventions.

### Testing
- Verify required repository structure.
- Verify the CI workflow executes on pull requests.
- Verify repository hygiene checks.
- Verify direct pushes to protected branches are restricted.

### Acceptance Criteria
- Repository structure is established.
- Initial CI workflow executes successfully.
- Pull request workflow is functional.
- Main branch protection is configured.

---

## Sprint 01B — Backend Foundation

**Branch:** `sprint/01b-backend-foundation`  
**Duration:** 4 working days  
**Dependencies:** 01A

### Objective
Establish the Django backend and its foundational infrastructure.

### Implementation Tasks

1. Initialize Django and Django REST Framework.
2. Configure modular Django settings for development and testing.
3. Establish the `/api/v1/` API namespace.
4. Configure PostgreSQL 18 and pgvector.
5. Configure Redis and Celery.
6. Establish initial backend health-check endpoints.
7. Implement standardized API error responses.
8. Configure structured request logging.
9. Integrate S3-compatible development storage.
10. Configure Docker and Docker Compose for backend services.
11. Establish pytest and pytest-django.
12. Integrate backend testing into CI.

### Testing
- Django configuration tests.
- Database connectivity tests.
- pgvector extension tests.
- Redis connectivity tests.
- Celery task execution tests.
- Health-check API tests.
- Backend CI tests.

### Acceptance Criteria
- Django starts successfully.
- PostgreSQL and Redis connections work.
- pgvector is enabled.
- Celery can execute a test task.
- Backend health checks return successful responses.
- Backend tests pass in CI.

---

## Sprint 01C — AI Service Foundation

**Branch:** `sprint/01c-ai-service-foundation`  
**Duration:** 3 working days  
**Dependencies:** 01A

### Objective
Establish the dedicated FastAPI AI microservice and its internal communication contract.

### Implementation Tasks

1. Initialize the FastAPI application.
2. Establish modular service and provider directories.
3. Configure environment-based settings.
4. Implement internal service authentication.
5. Implement health and model-status endpoints.
6. Establish standardized request and response schemas.
7. Configure Docker integration.
8. Integrate AI service tests into CI.

Actual model loading and inference are deferred to v0.3.0.

### Testing
- Service startup tests.
- Authentication tests.
- Request validation tests.
- Error response tests.
- Health endpoint tests.

### Acceptance Criteria
- FastAPI service starts successfully.
- Internal authentication works.
- Invalid requests are rejected.
- Service tests pass in CI.

---

## Sprint 01D — Web Application Foundation

**Status: Completed**  
**Branch:** `sprint/01d-web-foundation`  
**Duration:** 4 working days  
**Dependencies:** 01B

### Objective
Establish the React web application and its initial frontend architecture.

### Implementation Summary
- Initialized the web application with Vite, TypeScript, and React.
- Configured Tailwind CSS and the shadcn/ui style `Button` component.
- Established routing with `react-router-dom` and English, Filipino, and Hiligaynon localization via a context-based i18n provider with a language switcher.
- Established the fetch-based API client and an initial application status page that calls `GET /api/v1/health/`.
- Configured frontend testing with Vitest, jsdom, and Testing Library.
- CI: `web-checks` and `mobile-checks` jobs no longer skip when the manifests are missing; they fail instead.

### Implementation Tasks

1. Initialize React, TypeScript, and Vite.
2. Configure Tailwind CSS and shadcn/ui.
3. Establish reusable frontend components.
4. Configure application routing.
5. Establish the frontend API communication layer.
6. Configure API type generation from the backend OpenAPI specification.
7. Establish English, Filipino, and Hiligaynon localization support.
8. Implement an initial application status page.
9. Configure frontend testing and linting.
10. Integrate web tests and production builds into CI.

### Testing
- Component tests.
- API communication tests.
- Localization tests.
- TypeScript checks.
- Production build verification.

### Acceptance Criteria
- Web application starts successfully.
- Frontend communicates with the Django API.
- Localization framework works.
- Production build succeeds.
- CI web checks pass.

---

## Sprint 01E — Mobile Application Foundation

**Status: Completed**  
**Branch:** `sprint/01e-mobile-foundation`  
**Duration:** 4 working days  
**Dependencies:** 01B, 01D

### Objective
Establish the React Native mobile application and its communication with the shared backend.

### Implementation Summary
- Initialized the mobile application with Expo SDK 58, React Native, and TypeScript.
- Configured React Navigation with the backend connectivity and settings screens.
- Established reusable `Screen`, `Button`, `StatusCard`, and `LanguageSwitcher` components.
- Integrated the shared `@qualifil/api-client` workspace package.
- Implemented the mobile API communication layer with timeout and token support.
- Established secure token storage behind an `expo-secure-store` abstraction with a documented web fallback.
- Configured English, Filipino, and Hiligaynon localization with persisted locale selection.
- Configured `jest-expo`, React Native Testing Library, ESLint, and TypeScript checks in CI.

### Implementation Tasks

1. Initialize React Native using Expo.
2. Configure TypeScript and application navigation.
3. Establish reusable mobile components.
4. Integrate the shared API client.
5. Implement the mobile API communication layer.
6. Establish secure token storage abstraction.
7. Configure localization support.
8. Implement an initial backend connectivity screen.
9. Configure mobile testing and linting.
10. Integrate mobile checks into CI.

### Testing
- Component tests.
- API communication tests.
- Secure storage tests.
- Localization tests.
- Expo compatibility checks.
- Mobile build/export verification.

### Acceptance Criteria
- Mobile application starts successfully.
- Mobile application communicates with the Django API.
- Localization works.
- CI mobile checks pass.

**Release milestone:** Tag v0.1.0 after all five foundation sprints are completed.

---

# v0.2.0 — Authentication and Core Data Management

## Sprint 02A — Authentication

**Branch:** `sprint/02a-authentication`  
**Duration:** 5 working days  
**Dependencies:** 01B

### Objective
Implement secure user authentication and token management.

### Implementation Tasks

1. Implement the custom Django user model.
2. Configure SimpleJWT.
3. Implement registration and login services.
4. Implement access and refresh token handling.
5. Implement logout and token invalidation.
6. Implement password validation and secure password hashing.
7. Implement login throttling and account lockout.
8. Implement authenticated user information endpoints.
9. Establish authentication behavior for web and mobile clients.

### Testing
- Registration and login tests.
- Invalid credential tests.
- Token refresh and expiration tests.
- Logout and token invalidation tests.
- Password validation tests.
- Throttling and lockout tests.

### Acceptance Criteria
- Users can authenticate successfully.
- Invalid credentials are rejected.
- Refresh token lifecycle works.
- Authentication tests pass.

---

## Sprint 02B — Organizations and Role-Based Access Control

**Branch:** `sprint/02b-organizations-rbac`  
**Duration:** 4 working days  
**Dependencies:** 02A

### Objective
Establish LGU and barangay organizational structures and server-side authorization.

### Implementation Tasks

1. Implement LGU and barangay models.
2. Establish staff membership associations.
3. Define resident, barangay official, LGU personnel, and administrator roles.
4. Implement role-based permission classes.
5. Implement organization-scoped data access.
6. Establish reusable authorization and query-scoping patterns.
7. Implement initial organization data seeding.

### Testing
- Role permission tests.
- Organization association tests.
- Barangay data isolation tests.
- Cross-LGU access tests.
- Seed data tests.

### Acceptance Criteria
- Roles are enforced server-side.
- Users can only access authorized organizational data.
- Cross-barangay and cross-LGU access is denied.

---

## Sprint 02C — Audit Logging

**Branch:** `sprint/02c-audit-logging`  
**Duration:** 3 working days  
**Dependencies:** 02B

### Objective
Establish an auditable record of important system activities.

### Implementation Tasks

1. Implement the audit event model.
2. Implement centralized audit recording services.
3. Establish metadata sanitization.
4. Record authentication events.
5. Implement audit event retrieval for authorized LGU personnel.
6. Establish conventions for recording sensitive operations.

### Testing
- Audit event creation tests.
- Metadata sanitization tests.
- Audit access permission tests.
- Audit record immutability tests.

### Acceptance Criteria
- Important authentication activities are recorded.
- Sensitive values are excluded from audit metadata.
- Unauthorized users cannot access audit records.

---

## Sprint 02D — Resident Registration and Profiles

**Branch:** `sprint/02d-resident-profile`  
**Duration:** 5 working days  
**Dependencies:** 02C

### Objective
Implement resident registration, profile management, consent, and barangay approval.

### Implementation Tasks

1. Implement resident profile models.
2. Implement resident registration services.
3. Implement profile creation and editing.
4. Implement resident information validation.
5. Implement consent and privacy notice recording.
6. Implement resident approval and rejection workflows.
7. Implement barangay resident management endpoints.
8. Establish resident fact provenance.

### Testing
- Registration tests.
- Profile validation tests.
- Consent requirement tests.
- Approval and rejection tests.
- Barangay scoping tests.
- Sensitive information access tests.

### Acceptance Criteria
- Residents can register and manage their profiles.
- Barangay officials can review residents within their jurisdiction.
- Approval and rejection are recorded.
- Unapproved residents cannot access restricted functionality.

---

## Sprint 02E — Assistance Program Management

**Branch:** `sprint/02e-program-management`  
**Duration:** 6 working days  
**Dependencies:** 02D

### Objective
Implement LGU-managed assistance programs and structured eligibility criteria.

### Implementation Tasks

1. Implement assistance program categories.
2. Implement assistance program models.
3. Implement eligibility criterion definitions.
4. Implement documentary requirement definitions.
5. Establish a structured eligibility criteria catalog.
6. Implement program creation and editing.
7. Implement program publishing and archiving.
8. Implement immutable published program versions.
9. Implement program retrieval and filtering.
10. Establish program management permissions.

### Testing
- Program creation and editing tests.
- Criteria validation tests.
- Publishing and versioning tests.
- Archiving tests.
- Organization-scoped retrieval tests.

### Acceptance Criteria
- LGU administrators can create and publish assistance programs.
- Published program versions remain unchanged when drafts are edited.
- Residents can only access active programs within the appropriate LGU scope.

---

## Sprint 02F — Web Authentication and Program Management UI

**Branch:** `sprint/02f-web-auth-programs`  
**Duration:** 5 working days  
**Dependencies:** 02E

### Objective
Implement the web interface for staff authentication, resident approval, and assistance program management.

### Implementation Tasks

1. Implement staff login and logout screens.
2. Implement authenticated application routing.
3. Implement role-based frontend navigation.
4. Implement the resident approval queue.
5. Implement resident approval and rejection interfaces.
6. Implement assistance program listing.
7. Implement the program creation and editing interface.
8. Implement the eligibility criteria editor.
9. Implement program publishing and archiving controls.
10. Add translations for all new interface elements.

### Testing
- Authentication UI tests.
- Route protection tests.
- Program editor tests.
- Resident approval workflow tests.
- Localization tests.

### Acceptance Criteria
- Authorized staff can log in.
- Barangay officials can approve residents.
- LGU administrators can manage assistance programs.
- Unauthorized roles cannot access restricted interfaces.

---

## Sprint 02G — Mobile Authentication and Resident Profile UI

**Branch:** `sprint/02g-mobile-auth-profile`  
**Duration:** 5 working days  
**Dependencies:** 02E

### Objective
Implement the resident-facing authentication and profile experience.

### Implementation Tasks

1. Implement resident registration screens.
2. Implement login and logout screens.
3. Integrate secure token storage.
4. Implement resident profile viewing and editing.
5. Implement the pending approval screen.
6. Implement assistance program browsing.
7. Implement assistance program details.
8. Implement the language selector.

### Testing
- Registration and login tests.
- Token storage tests.
- Profile editing tests.
- Program browsing tests.
- Localization tests.
- Device-level workflow testing.

### Acceptance Criteria
- Residents can register and log in.
- Residents can manage their profiles.
- Residents can browse available assistance programs.
- Approval status is correctly reflected in the mobile application.

**Release milestone:** Tag v0.2.0 after all authentication and core data management sprints are completed.

---

# v0.3.0 — Eligibility Assessment and Program Matching

## Sprint 03A — Knowledge Base and Program Seeding

**Branch:** `sprint/03a-seed-knowledge-base`  
**Duration:** 5 working days  
**Dependencies:** 02E

### Objective
Establish the structured assistance program knowledge base and reproducible seed data.

### Implementation Tasks

1. Define the `programs_seed.json` structure.
2. Establish JSON schema validation.
3. Prepare initial Silay City assistance program entries.
4. Include AICS Medical Assistance, AICS Financial Assistance, and applicable scholarship programs.
5. Implement seed validation services.
6. Implement database import and export commands.
7. Implement seed synchronization and version tracking.
8. Establish protection for LGU-modified program records.

Only verified official program criteria should be treated as confirmed. Unverified information must remain explicitly marked for verification.

### Testing
- JSON schema tests.
- Seed validation tests.
- Import idempotency tests.
- Export and import consistency tests.
- Program version synchronization tests.

### Acceptance Criteria
- Seed data can be validated and imported.
- Repeated imports do not create duplicate records.
- LGU-modified records are protected from unintended overwrites.

---

## Sprint 03B — Eligibility Engine

**Branch:** `sprint/03b-eligibility-engine`  
**Duration:** 6 working days  
**Dependencies:** 02E

### Objective
Implement a deterministic and independently testable eligibility evaluation engine.

### Implementation Tasks

1. Define eligibility evaluation types and result structures.
2. Implement supported comparison operators.
3. Implement fact-to-criterion evaluation.
4. Implement the three-state result system:
   - Met
   - Unmet
   - Unknown
5. Implement overall eligibility determination.
6. Implement required and preferred criterion handling.
7. Establish engine versioning.
8. Implement golden test cases for seeded programs.
9. Enforce separation between eligibility logic and AI functionality.

### Testing
- Operator unit tests.
- Boundary condition tests.
- Missing information tests.
- Type validation tests.
- Deterministic evaluation tests.
- Property-based tests.
- Golden dataset tests.

### Acceptance Criteria
- Eligibility results are deterministic.
- Unknown information is never automatically classified as unmet.
- The engine operates independently of Django and AI services.
- All approved golden test cases pass.

---

## Sprint 03C — Assessment Snapshots and API

**Branch:** `sprint/03c-assessment-snapshots`  
**Duration:** 5 working days  
**Dependencies:** 03B, 02D

### Objective
Persist reproducible eligibility assessments and expose authorized assessment endpoints.

### Implementation Tasks

1. Implement the eligibility assessment model.
2. Store resident fact snapshots.
3. Store program version references.
4. Store individual criterion results.
5. Store overall assessment results.
6. Record the eligibility engine version.
7. Implement assessment services.
8. Implement assessment retrieval endpoints.
9. Establish assessment immutability.

### Testing
- Assessment creation tests.
- Snapshot immutability tests.
- Program version consistency tests.
- Resident data change tests.
- Assessment authorization tests.

### Acceptance Criteria
- Residents can receive eligibility assessments.
- Previous assessments remain unchanged when profile data changes.
- Assessment results can be reproduced using their stored snapshots.

---

## Sprint 03D — AI Embedding and Reranking Service

**Branch:** `sprint/03d-ai-embed-rerank`  
**Duration:** 6 working days  
**Dependencies:** 01C

### Objective
Implement embedding and reranking capabilities within the dedicated FastAPI AI service.

### Implementation Tasks

1. Implement model provider interfaces.
2. Implement a deterministic fake AI provider for testing.
3. Integrate Qwen/Qwen3-Embedding-0.6B.
4. Integrate Qwen/Qwen3-Reranker-0.6B.
5. Implement model loading and inference management.
6. Implement embedding API endpoints.
7. Implement reranking API endpoints.
8. Implement model loading status and error handling.
9. Establish model revision pinning.
10. Validate the selected model inference and reranking procedures.

### Testing
- API contract tests.
- Fake provider tests.
- Input validation tests.
- Model loading tests.
- Embedding dimension and normalization tests.
- Reranking tests.
- Manual real-model execution tests.

### Acceptance Criteria
- Embedding and reranking endpoints work.
- Fake provider tests pass in CI.
- Real model inference is demonstrated and documented.
- Model failures are handled without crashing the service.

---

## Sprint 03E — Program Embedding Synchronization

**Branch:** `sprint/03e-program-embeddings`  
**Duration:** 5 working days  
**Dependencies:** 03A, 03D

### Objective
Implement asynchronous embedding generation and synchronization for published assistance programs.

### Implementation Tasks

1. Implement the program embedding model.
2. Establish deterministic program serialization.
3. Implement the internal AI service client.
4. Implement Celery embedding tasks.
5. Trigger embedding generation when programs are published or updated.
6. Implement retry and failure handling.
7. Implement stale embedding detection.
8. Implement embedding reconciliation.
9. Implement program vector search using pgvector.
10. Establish model revision and source hash tracking.

### Testing
- Embedding task tests.
- Retry and failure tests.
- Stale vector tests.
- Program update tests.
- Vector search tests.
- LGU-scoped retrieval tests.

### Acceptance Criteria
- Published programs receive embeddings asynchronously.
- Updated programs receive updated embeddings.
- Stale vectors are not used in matching.
- Failed embedding tasks can be retried and reconciled.

---

## Sprint 03F — Program Matching Pipeline

**Branch:** `sprint/03f-matching-pipeline`  
**Duration:** 7 working days  
**Dependencies:** 03C, 03E

### Objective
Implement the program matching workflow using resident needs, embeddings, vector search, reranking, and eligibility assessment.

### Implementation Tasks

1. Implement the matching request and result models.
2. Implement the AI-assisted needs extraction endpoint.
3. Implement privacy-conscious input preprocessing.
4. Implement resident confirmation of extracted information.
5. Implement query embedding.
6. Implement pgvector candidate retrieval.
7. Integrate Qwen reranking.
8. Run deterministic eligibility assessment on matched programs.
9. Implement asynchronous matching tasks.
10. Implement matching status retrieval and polling.
11. Implement a fallback matching mechanism when AI services are unavailable.
12. Implement matching evaluation using a labelled dataset.

### Testing
- Matching pipeline tests.
- AI response validation tests.
- Prompt injection tests.
- PII redaction tests.
- Fallback behavior tests.
- Resident ownership tests.
- Matching evaluation tests.

### Acceptance Criteria
- Residents can submit a need and receive program matches.
- Matching results include eligibility assessments.
- Extracted resident facts require confirmation.
- Predefined category matching remains available without AI services.

---

## Sprint 03G — Eligibility Explanations

**Branch:** `sprint/03g-explanations`  
**Duration:** 5 working days  
**Dependencies:** 03C, 03D

### Objective
Implement multilingual explanations grounded in deterministic eligibility assessment results.

### Implementation Tasks

1. Implement the AI explanation endpoint.
2. Implement explanation request and response validation.
3. Implement criterion-level explanations.
4. Implement deterministic explanation templates.
5. Implement LLM explanation integration using Claude Haiku 5.5.
6. Implement fallback behavior when AI services are unavailable.
7. Implement explanation caching.
8. Establish Filipino and Hiligaynon language review.

### Testing
- Explanation schema tests.
- Criterion consistency tests.
- Invalid AI output tests.
- Fallback tests.
- Multilingual tests.
- Prohibited guarantee or approval language tests.

### Acceptance Criteria
- Explanations accurately reflect the assessment results.
- AI cannot modify eligibility statuses.
- Template explanations work when the AI service is unavailable.
- Explanations do not promise approval.

---

## Sprint 03H — Mobile Matching UI and LGU Rule Preview

**Branch:** `sprint/03h-mobile-matching-ui`  
**Duration:** 6 working days  
**Dependencies:** 03F, 03G

### Objective
Implement the resident matching experience and an LGU eligibility rule preview.

### Implementation Tasks

1. Implement the resident needs input screen.
2. Implement predefined assistance category selection.
3. Implement the extracted information confirmation screen.
4. Implement the matching results screen.
5. Implement asynchronous result polling.
6. Implement eligibility result cards.
7. Implement criterion-level assessment details.
8. Implement multilingual explanations.
9. Implement the AI degradation indicator.
10. Implement the LGU rule preview endpoint and web interface.

### Testing
- Mobile component tests.
- Matching workflow tests.
- Assessment display tests.
- Language tests.
- Rule preview tests.
- Preview non-persistence tests.

### Acceptance Criteria
- Residents can complete the matching workflow on mobile.
- Eligibility results and explanations are displayed correctly.
- LGU administrators can preview eligibility rules.
- Preview operations do not create permanent assessment records.

**Release milestone:** Tag v0.3.0 after all eligibility and matching sprints are completed.

---

# v0.4.0 — Document Processing and Application Management

## Sprint 04A — Document Storage and Upload

**Branch:** `sprint/04a-document-upload`  
**Duration:** 6 working days  
**Dependencies:** 02D

### Objective
Implement secure resident document uploading and private document storage.

### Implementation Tasks

1. Implement the document model and document type catalog.
2. Integrate S3-compatible storage.
3. Implement file type and file size validation.
4. Implement file content verification.
5. Implement secure file naming and storage paths.
6. Implement image preprocessing for metadata removal.
7. Implement encrypted storage for sensitive extracted text.
8. Implement document upload, retrieval, and deletion endpoints.
9. Implement permission-checked document access.

### Testing
- File upload tests.
- Invalid file tests.
- File size restriction tests.
- Storage permission tests.
- Document ownership tests.
- Secure download tests.

### Acceptance Criteria
- Residents can upload supported documents.
- Unauthorized users cannot access another resident's documents.
- Documents are stored privately.
- File validation is enforced server-side.

---

## Sprint 04B — OCR Processing

**Branch:** `sprint/04b-ocr-pipeline`  
**Duration:** 6 working days  
**Dependencies:** 04A

### Objective
Implement asynchronous document text extraction using Tesseract OCR.

### Implementation Tasks

1. Integrate Tesseract OCR.
2. Configure English and Filipino OCR language support.
3. Implement image preprocessing.
4. Implement PDF text extraction processing.
5. Implement document extraction models.
6. Implement document-specific field parsers.
7. Implement asynchronous OCR tasks using Celery.
8. Implement OCR processing status and error handling.
9. Establish an OCR evaluation dataset.

### Testing
- OCR unit tests.
- Synthetic document tests.
- Text extraction tests.
- Low-quality image tests.
- Task retry tests.
- Processing failure tests.

### Acceptance Criteria
- Uploaded documents can be processed asynchronously.
- Extracted text and structured fields are stored securely.
- Failed OCR operations produce meaningful error states.
- OCR performance is measured using a controlled test dataset.

---

## Sprint 04C — Document Validation

**Branch:** `sprint/04c-document-validation`  
**Duration:** 6 working days  
**Dependencies:** 04B

### Objective
Implement rule-based document completeness, readability, consistency, and validity checks.

### Implementation Tasks

1. Implement document readability checks.
2. Implement required field completeness checks.
3. Implement extracted information consistency checks.
4. Implement document expiration and validity checks.
5. Implement document validation result records.
6. Implement document verification services.
7. Implement document validation retrieval endpoints.
8. Establish the distinction between verified, flagged, and unknown results.

### Testing
- Document validation tests.
- Name normalization tests.
- Date parsing tests.
- Expiration tests.
- Missing field tests.
- Validation boundary tests.
- Regression tests.

### Acceptance Criteria
- Documents are evaluated against defined validation rules.
- Inconsistent or incomplete documents are flagged.
- Unknown results are not automatically treated as failures.
- Automated validation never guarantees document authenticity or automatically rejects an applicant.

---

## Sprint 04D — Requirement Gap Analysis and Action Plans

**Branch:** `sprint/04d-gap-action-plan`  
**Duration:** 5 working days  
**Dependencies:** 03G, 04C

### Objective
Identify missing eligibility information and documentary requirements, then provide actionable guidance.

### Implementation Tasks

1. Implement deterministic requirement gap analysis.
2. Identify unmet eligibility criteria.
3. Identify unknown eligibility criteria.
4. Identify missing documentary requirements.
5. Identify flagged documents.
6. Implement requirement gap retrieval endpoints.
7. Implement AI-assisted action plan generation.
8. Implement response validation and deterministic fallback templates.
9. Implement action plan caching and regeneration.

### Testing
- Gap identification tests.
- Document coverage tests.
- Action plan validation tests.
- AI failure tests.
- Cache invalidation tests.

### Acceptance Criteria
- Residents can see what information and documents remain incomplete.
- Each identified gap has a corresponding action.
- AI-generated plans cannot introduce unsupported program requirements.

---

## Sprint 04E — Application Submission and Status Tracking

**Branch:** `sprint/04e-applications`  
**Duration:** 6 working days  
**Dependencies:** 04D

### Objective
Implement the application lifecycle and resident application tracking.

### Implementation Tasks

1. Implement the application model.
2. Implement application-document associations.
3. Implement application status history.
4. Define allowed application state transitions.
5. Implement application creation.
6. Implement document attachment and removal.
7. Implement application submission validation.
8. Implement application withdrawal.
9. Implement application status retrieval.
10. Preserve assessment and requirement snapshots at submission.

### Testing
- Application creation tests.
- State transition tests.
- Submission validation tests.
- Duplicate submission tests.
- Application ownership tests.
- Status history tests.

### Acceptance Criteria
- Residents can submit complete applications.
- Incomplete applications cannot bypass required validation.
- Application history is recorded.
- Residents can track their application status.

---

## Sprint 04F — Barangay Document Review and Escalation

**Branch:** `sprint/04f-brgy-document-review`  
**Duration:** 5 working days  
**Dependencies:** 04E, 04C

### Objective
Implement manual barangay document review and escalation to authorized LGU personnel.

### Implementation Tasks

1. Implement document review records.
2. Implement barangay document review services.
3. Implement document verification decisions.
4. Implement rejection and resubmission handling.
5. Implement escalation to LGU personnel.
6. Implement review endpoints.
7. Implement the web-based barangay review queue.
8. Integrate review decisions with application status transitions.
9. Record review actions in the audit system.

### Testing
- Barangay permission tests.
- LGU escalation tests.
- Document review transition tests.
- Concurrent review tests.
- Audit tests.

### Acceptance Criteria
- Barangay officials can review documents within their jurisdiction.
- Flagged documents can be escalated.
- Review decisions are recorded.
- Application statuses update appropriately.

---

## Sprint 04G — Mobile Document and Application UI

**Branch:** `sprint/04g-mobile-documents-apps`  
**Duration:** 6 working days  
**Dependencies:** 04D, 04E

### Objective
Implement the resident-facing document and application workflow on mobile.

### Implementation Tasks

1. Implement requirement gap screens.
2. Implement action plan screens.
3. Implement camera and gallery document uploads.
4. Implement upload progress and retry handling.
5. Implement document processing status indicators.
6. Implement document reuse selection.
7. Implement application submission review screens.
8. Implement application history and status timelines.
9. Implement slow network and error states.

### Testing
- Upload component tests.
- Document status tests.
- Application submission tests.
- Missing requirement tests.
- Device-level workflow tests.

### Acceptance Criteria
- Residents can upload and manage documents.
- Residents can complete the application submission workflow.
- Application status and document review results are visible on mobile.

**Release milestone:** Tag v0.4.0 after all document and application management sprints are completed.

---

# v0.5.0 — LGU Review and System Integration

## Sprint 05A — Applicant Review List

**Branch:** `sprint/05a-applicant-review-list`  
**Duration:** 6 working days  
**Dependencies:** 04F

### Objective
Implement the LGU applicant review interface with eligibility and document verification information.

### Implementation Tasks

1. Establish the applicant review module.
2. Implement applicant grouping based on approved eligibility and document readiness criteria.
3. Implement the applicant review query services.
4. Implement filtering by program, barangay, and criterion status.
5. Implement applicant detail retrieval.
6. Display eligibility and document verification evidence.
7. Implement the LGU review interface.
8. Implement a barangay read-only review interface.

No ranking weights or automated applicant selection should be introduced without an approved selection methodology.

### Testing
- Applicant grouping tests.
- Filtering tests.
- Authorization tests.
- Cross-barangay isolation tests.
- Cross-LGU isolation tests.
- Applicant data privacy tests.

### Acceptance Criteria
- LGU personnel can review applicants for their programs.
- Barangay officials can view authorized applicants within their jurisdiction.
- The interface provides supporting eligibility and document information.
- No unauthorized ranking or selection occurs.

---

## Sprint 05B — LGU Selection and Export

**Branch:** `sprint/05b-lgu-selection`  
**Duration:** 6 working days  
**Dependencies:** 05A

### Objective
Implement authorized LGU selection decisions and application data export.

### Implementation Tasks

1. Implement selection decision records.
2. Implement selection and non-selection services.
3. Implement decision justification requirements.
4. Implement individual and bulk decision operations.
5. Integrate selection decisions with application status transitions.
6. Implement the LGU application export functionality.
7. Implement CSV export validation and sanitization.
8. Implement export audit records.
9. Implement the LGU selection interface.

### Testing
- Selection authorization tests.
- Decision history tests.
- Bulk decision tests.
- CSV export tests.
- CSV formula injection tests.
- Cross-LGU access tests.

### Acceptance Criteria
- Authorized LGU personnel can record final selection decisions.
- Decisions are auditable.
- Unauthorized users cannot select applicants or export restricted data.
- Residents can view their own decision status.

---

## Sprint 05C — Distribution Tracking

**Branch:** `sprint/05c-distribution`  
**Duration:** 4 working days  
**Dependencies:** 05B

### Objective
Implement the tracking of assistance distribution to selected applicants.

### Implementation Tasks

1. Implement distribution records.
2. Implement distribution status management.
3. Implement barangay release recording.
4. Implement unclaimed assistance recording.
5. Implement distribution summary endpoints.
6. Implement the barangay distribution interface.
7. Implement LGU distribution summaries.
8. Integrate distribution status into resident application timelines.

### Testing
- Distribution creation tests.
- Release authorization tests.
- Duplicate release tests.
- Unclaimed assistance tests.
- Summary calculation tests.

### Acceptance Criteria
- Selected applications can be tracked through distribution.
- Authorized barangay personnel can record releases.
- LGU personnel can view distribution summaries.
- Residents can view their own distribution status.

---

## Sprint 05D — Messaging and Notifications

**Branch:** `sprint/05d-messaging`  
**Duration:** 6 working days  
**Dependencies:** 04E

### Objective
Implement internal messaging and application-related notifications.

### Implementation Tasks

1. Implement conversation models.
2. Implement message models.
3. Implement notification records.
4. Establish conversation participation permissions.
5. Implement message sending and retrieval.
6. Implement unread message tracking.
7. Implement notification retrieval and read status.
8. Trigger notifications for important application events.
9. Implement web messaging interfaces.
10. Implement mobile messaging interfaces.
11. Implement foreground polling for new messages and notifications.

### Testing
- Messaging authorization tests.
- Conversation ownership tests.
- Message retrieval tests.
- Notification tests.
- Unread count tests.
- Cross-barangay access tests.

### Acceptance Criteria
- Residents and authorized staff can exchange messages.
- Application status changes can generate notifications.
- Users cannot access conversations outside their authorization scope.

---

## Sprint 05E — Security Hardening

**Branch:** `sprint/05e-security-hardening`  
**Duration:** 6 working days  
**Dependencies:** All feature sprints

### Objective
Conduct a comprehensive security review and address identified vulnerabilities before deployment.

### Implementation Tasks

1. Conduct a system threat assessment.
2. Review authentication and authorization.
3. Review barangay and LGU data isolation.
4. Conduct IDOR and access control testing.
5. Review document upload and storage security.
6. Review sensitive information handling.
7. Review API security and input validation.
8. Review environment secrets and service authentication.
9. Configure security headers and CORS restrictions.
10. Review dependency vulnerabilities.
11. Implement additional security tests.
12. Address identified high-priority findings.

### Testing
- Authorization regression tests.
- IDOR tests.
- Security header tests.
- Dependency scanning.
- Input validation tests.
- Sensitive data exposure tests.
- Authentication security tests.

### Acceptance Criteria
- No unresolved critical or high-priority security findings remain.
- Authorization tests pass.
- Sensitive information is protected.
- Security review findings are documented and addressed.

---

## Sprint 05F — System Integration and Performance Testing

**Branch:** `sprint/05f-integration-perf-testing`  
**Duration:** 7 working days  
**Dependencies:** 05E

### Objective
Validate the complete QUALIFIL system through end-to-end testing, integration testing, and performance evaluation.

### Implementation Tasks

1. Integrate the resident, barangay, and LGU workflows.
2. Implement complete end-to-end test scenarios.
3. Test web and mobile API integration.
4. Test Django and FastAPI communication.
5. Test Celery and Redis background processing.
6. Test PostgreSQL and pgvector operations.
7. Test document upload and OCR workflows.
8. Test AI service failure and fallback behavior.
9. Conduct performance testing.
10. Evaluate embedding and reranking performance.
11. Evaluate eligibility engine accuracy.
12. Evaluate OCR extraction performance.
13. Validate system behavior under the expected server configurations.

### Testing
- End-to-end tests.
- Integration tests.
- Regression tests.
- API load tests.
- Database performance tests.
- AI service performance tests.
- Mobile workflow tests.
- 8 GB and 16 GB server resource evaluation.

### Acceptance Criteria
- Complete resident-to-LGU workflows pass.
- Critical integrations work reliably.
- Performance results are measured and documented.
- No unresolved critical regression remains.

---

## Sprint 05G — Deployment Preparation and Release

**Branch:** `sprint/05g-deployment-prep`  
**Duration:** 5 working days  
**Dependencies:** 05F

### Objective
Prepare QUALIFIL for controlled staging and production deployment.

### Implementation Tasks

1. Finalize production and staging deployment configurations.
2. Configure application process management.
3. Configure reverse proxy and HTTPS.
4. Establish production database migration procedures.
5. Implement database backup and restoration procedures.
6. Establish container image build and release workflows.
7. Implement deployment health checks.
8. Implement deployment smoke tests.
9. Conduct a rollback test.
10. Conduct a database restoration drill.
11. Prepare mobile testing builds.
12. Finalize deployment documentation.
13. Conduct final release verification.

### Testing
- Production configuration validation.
- Staging deployment tests.
- Health-check tests.
- Backup and restoration tests.
- Rollback tests.
- Release workflow tests.
- Final end-to-end smoke tests.

### Acceptance Criteria
- QUALIFIL can be deployed to staging.
- Deployment and rollback procedures are verified.
- Database backup and restoration are tested.
- Final release checks pass.
- v0.5.0 is ready for controlled deployment.

**Release milestone:** Tag v0.5.0 after all integration, security, and deployment acceptance criteria are satisfied.

---

# 4. Release Completion Requirements

A release must not be tagged solely because its scheduled sprints have ended.

Before marking a release complete:

- All included sprints must be completed and merged.
- Required automated tests must pass.
- Critical integration workflows must be verified.
- No unresolved critical defects may remain.
- Relevant acceptance criteria must be satisfied.
- The release must be reviewed by the development team.

The release is considered complete when its functionality is implemented, tested, integrated, and approved for the next development milestone.

---

# 5. Sprint Execution Notes

1. A sprint must not begin before its critical dependencies are merged.
2. Each sprint must have a dedicated GitHub branch.
3. Large tasks may be divided into smaller sprint subdivisions.
4. Backend, web, mobile, and AI work may proceed in parallel when their dependencies and API contracts are established.
5. Every sprint must include testing and integration work.
6. Changes to existing functionality must include regression tests.
7. Any change to the approved architecture or technical scope must be reviewed before implementation.
8. Features outside the approved thesis scope must not be introduced without an explicit decision.
9. A sprint is complete only after its acceptance criteria and Definition of Done are satisfied.