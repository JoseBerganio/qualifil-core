# QUALIFIL — Backend Module Responsibilities

## Purpose

This document defines the intended responsibilities and boundaries of the Django backend applications.

The project uses a modular monolith. Modules are separated by business responsibility, not deployed as independent services.

## 1. accounts

Responsible for:
- User accounts
- Authentication integration
- JWT-related configuration
- Account activation and deactivation
- Password and account security workflows

Must not own resident assistance applications or program eligibility rules.

## 2. organizations

Responsible for:
- LGU and barangay organizational records
- Organization relationships
- User-to-organization assignments
- Role and permission assignments
- Organization-level access boundaries

Must not duplicate Django's authentication responsibilities.

## 3. residents

Responsible for:
- Resident profiles
- Resident demographic and household information required by the system
- Resident profile updates
- Resident information validation

Must not decide final assistance program eligibility.

## 4. programs

Responsible for:
- Assistance program records
- Program descriptions
- Program requirements
- Eligibility criteria configuration
- Program publication and archival
- Program version management
- Program seed import and synchronization

Program changes must preserve historical information needed by prior assessments and applications.

## 5. eligibility

Responsible for:
- Deterministic eligibility evaluation
- Criterion-level results
- `Met`, `Unmet`, and `Unknown` outcomes
- Assessment snapshots
- Rule and engine version references
- Eligibility result explanations based on actual rule outcomes

Must not use an LLM as the authoritative eligibility evaluator.

## 6. documents

Responsible for:
- Document metadata
- Upload authorization
- Object storage integration
- OCR task orchestration
- OCR result records
- Readability and completeness validation
- Document review status

Must not claim that OCR or consistency checks establish authenticity.

## 7. applications

Responsible for:
- Application creation and submission
- Application status
- Program and resident associations
- Required document associations
- Application lifecycle constraints

Must not independently perform LGU final selection decisions.

## 8. reviews

Responsible for:
- Barangay review workflows
- LGU review workflows
- Review assignments
- Review comments and findings
- Escalation workflows
- Recorded decisions and decision metadata

Must enforce the permissions of the reviewing organization and role.

## 9. distributions

Responsible for:
- Assistance distribution records
- Distribution status
- Distribution dates
- Authorized distribution updates
- Distribution reporting

Must preserve a record of important changes.

## 10. audit

Responsible for:
- Recording important system actions
- Recording administrative changes
- Recording review and decision events
- Recording relevant actor, timestamp, and target information

Audit records should be protected against ordinary unauthorized modification.

## 11. notifications

Responsible for:
- Notification records
- Notification delivery orchestration
- Notification preferences where included in scope
- Delivery status and retry handling

Notifications must not become the authoritative source of application status.

## Dependency Rules

- `accounts` provides identity information to other modules.
- `organizations` provides organizational scope and assignments.
- `residents` provides resident information to eligibility and applications.
- `programs` provides program definitions and criteria to eligibility and matching.
- `eligibility` evaluates program criteria using resident facts.
- `applications` references residents, programs, assessments, and documents.
- `documents` provides document records to applications and reviews.
- `reviews` manages authorized review workflows.
- `distributions` records assistance distribution after the relevant authorization.
- `audit` receives events from modules without owning their business logic.
- `notifications` communicates events without replacing the source records.

## Boundary Rules

1. A module should own its models and business rules.
2. Other modules should use documented service functions or interfaces instead of modifying another module's records directly.
3. Avoid circular imports and circular application dependencies.
4. Keep API serializers focused on input/output validation.
5. Keep business rules in service or domain layers.
6. Use database transactions for multi-record operations that must succeed or fail together.
7. Use explicit events or task interfaces for asynchronous work.
8. Do not introduce a separate microservice for every Django application.