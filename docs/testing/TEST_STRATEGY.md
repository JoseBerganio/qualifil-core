# QUALIFIL — Test Strategy

## 1. Purpose

This document defines the minimum testing approach for QUALIFIL.

Testing must verify both technical correctness and the system's critical business rules.

## 2. Test Levels

### Unit Tests

Test individual functions, services, validators, and business rules in isolation.

Examples:
- Eligibility criterion evaluation
- Unknown-value handling
- Program validation
- Application status transitions
- Permission checks
- Document validation rules

### Integration Tests

Test interactions between application modules and infrastructure.

Examples:
- Django ORM operations
- API-to-database operations
- Celery task execution
- Object storage interactions
- Django-to-AI-service requests
- pgvector query behavior

### API Tests

Test:
- Request validation
- Authentication
- Authorization
- Response structure
- Error responses
- Pagination and filtering
- Role and organization restrictions

### End-to-End Tests

Test complete user workflows across the application.

Examples:
- Resident registration and login
- Program discovery
- Eligibility assessment
- Document upload
- Application submission
- Barangay review
- LGU review and selection
- Distribution recording

## 3. Backend Test Requirements

Use pytest with Django test utilities.

Backend tests should cover:
- Model constraints
- Service-layer logic
- API endpoints
- Permission enforcement
- Database transactions
- Assessment snapshot immutability
- Application lifecycle rules
- Audit event creation

## 4. Eligibility Test Requirements

Eligibility is a high-priority business domain.

Test:
- A criterion that is satisfied returns `Met`.
- A criterion that is not satisfied returns `Unmet`.
- Missing or insufficient information returns `Unknown`.
- `Unknown` is not silently converted to `Unmet`.
- Every assessment references the correct program version.
- Every assessment records the rule and engine versions.
- Criterion-level outcomes are preserved.
- Reassessing after a program change does not overwrite an earlier snapshot.
- AI responses cannot change the deterministic outcome.

Use representative fixtures and boundary-value tests for each criterion type.

## 5. AI Service Test Requirements

Test:
- Input validation
- Model loading behavior
- Embedding output shape and type
- Reranking input and output validation
- Timeout behavior
- Model-unavailable behavior
- Malformed response handling
- Sensitive data handling
- Fallback behavior where defined

Do not make automated tests depend on paid live model calls unless a separately controlled integration test explicitly requires them.

Use mocks or deterministic test doubles for ordinary CI.

## 6. OCR and Document Test Requirements

Test:
- Permitted file types
- File size restrictions
- Invalid and corrupted files
- OCR success and failure
- Empty or unreadable OCR output
- Language configuration
- Duplicate task execution
- Retry behavior
- Document-to-application associations
- Reviewer access permissions

OCR output must not be treated as proof of authenticity.

## 7. Web and Mobile Test Requirements

Test:
- Form validation
- Authentication flows
- API error handling
- Loading and empty states
- Program discovery
- Eligibility result presentation
- Document upload
- Application status display
- Role-specific navigation

Client-side validation is for usability. The backend must independently validate all important operations.

## 8. Security Tests

Test:
- Unauthenticated access rejection
- Unauthorized role rejection
- Cross-organization data access prevention
- Invalid token handling
- File upload restrictions
- Sensitive data exposure
- Administrative operation authorization
- Audit record generation for important actions

## 9. CI Requirements

Every sprint pull request should:
- Run relevant automated tests.
- Run applicable linting and static checks.
- Build affected applications.
- Report failures clearly.
- Pass required checks before merge.

## 10. Test Data

Use synthetic test data.

Do not place real resident personal information, government identification numbers, or private documents in test fixtures.

## 11. Definition of Done

A feature is not complete until:
- Relevant tests exist.
- Tests pass locally and in CI.
- Important failure cases are covered.
- Authorization is tested.
- Documentation is updated where necessary.
- Acceptance criteria are satisfied.