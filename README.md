# QUALIFIL

**A Cross-Platform Local Government Assistance Information and Application Management System**

QUALIFIL is a web and mobile system designed to help residents discover local government assistance programs, understand potential eligibility, prepare requirements, and track applications. It also provides authorized barangay and LGU personnel with tools to manage programs, review applications, and monitor assistance distribution.

## Project Status

Development is organized into five target releases:

- **v0.1.0** — Project Foundation
- **v0.2.0** — Authentication and Core Data
- **v0.3.0** — Eligibility and Program Matching
- **v0.4.0** — Documents and Applications
- **v0.5.0** — LGU Review and System Integration

See `SPRINT.md` for the sprint breakdown and `PROGRESS.md` for implementation status.

## Core Capabilities

### Resident Features
- Resident registration and profile management
- Assistance program discovery
- Potential eligibility assessment
- Eligibility explanations and requirement gap analysis
- Document upload and OCR-assisted processing
- Application submission and status tracking

### Barangay Features
- Resident and application review
- Document completeness review
- Application verification workflow
- Escalation of applications to the appropriate LGU office

### LGU Features
- Assistance program creation and management
- Eligibility rule configuration
- Applicant review and selection
- Assistance distribution tracking
- Program and application monitoring

### AI-Assisted Features
- Semantic program discovery
- Retrieval and reranking of relevant program information
- OCR-assisted document processing
- AI-generated explanations of program requirements

AI-assisted features support information retrieval and interpretation. They do not make final eligibility or approval decisions.

## Technology Stack

### Web Application
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

### Mobile Application
- React Native
- Expo

### Backend
- Python
- Django
- Django REST Framework
- Django ORM
- PostgreSQL 18
- pgvector
- SimpleJWT

### Background Processing
- Celery
- Redis

### AI Service
- FastAPI
- Claude Haiku 5.5
- Qwen/Qwen3-Embedding-0.6B
- Qwen/Qwen3-Reranker-0.6B

### Document Processing
- Tesseract OCR
- S3-compatible object storage

### Development and Deployment
- Docker
- Docker Compose
- GitHub Actions
- pytest

## Architecture Overview

QUALIFIL uses a modular Django monolith for its primary backend and a separate FastAPI service for AI-related operations.

The web and mobile applications communicate with the Django REST API. The Django backend manages authentication, users, organizations, programs, eligibility assessments, documents, applications, and review workflows.

The AI service handles model-dependent operations such as semantic interpretation, embedding generation, reranking, and AI-assisted explanations. It does not own the authoritative program, resident, or application records.

Celery workers handle asynchronous tasks such as OCR processing, embedding generation, and other background operations.

PostgreSQL is the primary system of record. pgvector stores vector representations associated with program information.

## Important Business Rules

1. An eligibility assessment indicates potential eligibility, not guaranteed approval.
2. Eligibility evaluation must be deterministic and independent of AI-generated conclusions.
3. Eligibility criteria must support three outcomes: `Met`, `Unmet`, and `Unknown`.
4. An `Unknown` result must not automatically be treated as `Unmet`.
5. Final applicant approval and selection remain the responsibility of authorized LGU personnel.
6. AI-generated explanations must not override eligibility engine results.
7. Document processing checks completeness, readability, and consistency. It does not establish document authenticity.
8. Program information is maintained by participating LGUs.
9. External government database integrations are not assumed to be available.
10. Assessment records must preserve the program version, resident facts used, rule version, engine version, and individual criterion results at the time of assessment.

## Repository Structure

The repository should follow this structure. Individual sprint branches may introduce modules incrementally.

```text
qualifil/
├── backend/
│   ├── config/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── organizations/
│   │   ├── residents/
│   │   ├── programs/
│   │   ├── eligibility/
│   │   ├── documents/
│   │   ├── applications/
│   │   ├── reviews/
│   │   ├── distributions/
│   │   ├── audit/
│   │   └── notifications/
│   ├── tests/
│   ├── manage.py
│   └── requirements/
├── ai-service/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── schemas/
│   └── tests/
├── web/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   └── public/
├── mobile/
│   ├── app/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   └── assets/
├── knowledge-base/
│   └── programs_seed.json
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── api/
│   ├── runbooks/
│   ├── security/
│   └── testing/
├── scripts/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── PROGRESS.md
├── README.md
└── SPRINT.md
```

The exact internal package structure may evolve, but module boundaries and responsibilities must remain clear.

## Getting Started

### Prerequisites

Install the following tools:

- Git
- Python
- Node.js and npm
- Docker and Docker Compose
- PostgreSQL-compatible tooling, if running the database outside Docker

Use the versions specified by the project's dependency and container configuration once those files are established.

### Initial Setup

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Configure the local environment variables.
4. Start the infrastructure services using Docker Compose.
5. Install backend dependencies.
6. Apply Django database migrations.
7. Install web dependencies.
8. Install mobile dependencies.
9. Start the required development servers.

The exact commands should be added here when the initial Docker Compose, backend dependency, web package, and mobile package files are implemented.

## Development Workflow

Each sprint subdivision must have its own Git branch.

Branch naming convention:

```text
sprint/01a-project-structure
sprint/01b-backend-foundation
sprint/01c-ai-service-foundation
```

General workflow:

1. Start from the latest approved `main` branch.
2. Create the branch assigned to the sprint.
3. Implement only the scope assigned to that sprint.
4. Add or update automated tests.
5. Run the applicable test suites locally.
6. Open a pull request.
7. Pass the required GitHub Actions checks.
8. Complete code review.
9. Merge the approved changes into the integration target.
10. Update `PROGRESS.md` and `CHANGELOG.md` when applicable.

Do not begin dependent sprint work until its required dependencies have been merged or otherwise made available through an agreed integration branch.

## Testing

Automated testing is required throughout development.

- Backend: pytest and Django test utilities
- AI service: pytest
- Web: the selected TypeScript-compatible test runner
- Mobile: the selected React Native-compatible test runner
- Integration: API and cross-service tests

Tests should cover business rules, authorization, data validation, API behavior, error handling, and critical workflows.

## Security

- Never commit secrets, credentials, private keys, or production environment files.
- Enforce authorization on the backend.
- Validate uploaded files and restrict permitted file types and sizes.
- Keep AI service credentials on the server side.
- Do not expose internal services directly to public clients.
- Record important administrative and review actions in audit logs.
- Apply appropriate access controls to resident information and uploaded documents.

## Scope Limitations

The initial project scope does not assume:

- Direct integration with external DSWD or other government databases
- External identity verification
- Payment processing
- Automated determination of document authenticity
- AI-controlled final approval or applicant selection

Any expansion of these capabilities requires explicit project approval and appropriate technical, legal, and operational review.

## Documentation

- `SPRINT.md` — Sprint plan and acceptance criteria
- `PROGRESS.md` — Current implementation status
- `CHANGELOG.md` — Version history and notable changes
- `docs/architecture/` — Architecture and module responsibilities
- `docs/adr/` — Architecture Decision Records
- `docs/api/` — API documentation
- `docs/runbooks/` — Development and deployment procedures
- `docs/security/` — Security documentation
- `docs/testing/` — Test strategy and evaluation records

## License

This project is distributed under the MIT License. See `LICENSE` for details.
