# ADR 0001: Modular Monolith with a Dedicated AI Service

- Status: Accepted
- Date: YYYY-MM-DD
- Decision owners: QUALIFIL Development Team

## Context

QUALIFIL requires multiple business capabilities, including resident management, program management, eligibility evaluation, document processing, application workflows, and LGU review.

The system also requires AI-assisted interpretation, embedding generation, semantic retrieval, and reranking.

Separating every business domain into an independent microservice would introduce additional deployment, communication, and operational complexity.

At the same time, AI model dependencies have different runtime and resource requirements from the primary business API.

## Decision

Use a modular Django monolith for the primary backend and a dedicated FastAPI microservice for AI-related operations.

The Django backend owns authoritative business records and business rules.

The FastAPI service handles AI-related processing and returns derived outputs to the backend.

The web and mobile clients communicate with the Django REST API.

## Consequences

### Positive
- Business domains remain organized into clear modules.
- The primary backend has one authoritative business-data boundary.
- AI dependencies can be isolated from the main backend.
- Web and mobile clients share the same API and business rules.
- The architecture avoids premature microservice proliferation.

### Negative
- Module boundaries must be actively maintained.
- The Django backend remains a substantial application.
- Internal AI communication requires authentication, timeouts, and error handling.
- AI infrastructure may need separate deployment and resource allocation.

## Constraints

- The AI service cannot make authoritative eligibility or approval decisions.
- The AI service cannot directly mutate authoritative business records.
- The Django backend validates and stores authoritative results.
- Clients cannot directly access internal AI endpoints.

## Review Conditions

Reconsider this decision if:
- A business module develops independently scalable requirements.
- A module requires a distinct deployment or availability boundary.
- Operational evidence shows that the current structure is limiting development or reliability.

Do not split modules into services solely to increase the number of services.