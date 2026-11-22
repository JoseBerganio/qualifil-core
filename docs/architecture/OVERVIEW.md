# QUALIFIL — System Architecture

## 1. Architectural Style

QUALIFIL uses a modular monolithic backend supported by a dedicated AI microservice.

The primary backend is built with Django and Django REST Framework. Business domains are separated into Django applications with clear responsibilities and controlled dependencies.

The AI service is built with FastAPI. It handles model-dependent operations and communicates with the backend through private service-to-service requests.

The web and mobile applications use the same public backend API.

## 2. High-Level Components

### Web Client
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

Responsibilities:
- Resident-facing web interface
- Barangay and LGU management interfaces
- API requests and client-side state
- Form validation and user feedback
- Presentation of eligibility and application results

The web client must not connect directly to PostgreSQL, Redis, object storage credentials, or internal AI model endpoints.

### Mobile Client
- React Native
- Expo

Responsibilities:
- Resident-facing mobile interface
- Authentication and profile management
- Program discovery and eligibility result presentation
- Document upload
- Application submission and tracking

The mobile client uses the same public API and business rules as the web client.

### Django Backend
- Python
- Django
- Django REST Framework
- Django ORM
- SimpleJWT

Responsibilities:
- Authentication and authorization
- Resident and organization records
- Assistance program management
- Eligibility rule execution
- Assessment snapshots
- Application lifecycle
- Document metadata and review
- Audit logs
- LGU and barangay workflows
- API validation and orchestration

The Django backend is the authoritative owner of application business data.

### AI Service
- FastAPI
- Claude Haiku 5.5
- Qwen/Qwen3-Embedding-0.6B
- Qwen/Qwen3-Reranker-0.6B

Responsibilities:
- AI-assisted interpretation of program information
- Embedding generation
- Semantic retrieval support
- Reranking
- AI-assisted explanations

The AI service must not independently approve residents, change eligibility results, or write authoritative business records.

### PostgreSQL and pgvector

PostgreSQL is the primary database.

It stores:
- User and resident records
- Organizations and roles
- Assistance programs and versions
- Eligibility criteria
- Assessment snapshots
- Document metadata
- Applications
- Reviews and decisions
- Distribution records
- Audit logs
- Vector embeddings through pgvector

### Redis and Celery

Redis supports background task processing and related infrastructure needs.

Celery workers handle asynchronous operations, including:
- OCR processing
- Embedding generation
- Program embedding synchronization
- Other long-running tasks

### Object Storage

An S3-compatible storage service stores uploaded documents and generated files.

The backend controls authorization and access to stored objects. Clients must not receive permanent unrestricted storage credentials.

## 3. Request and Processing Flows

### Standard API Request

1. The web or mobile client sends an authenticated request to Django REST Framework.
2. Django validates the token and permissions.
3. The responsible application module validates the request.
4. Django performs the required business operation.
5. PostgreSQL stores or retrieves authoritative records.
6. Django returns a structured response to the client.

### Eligibility Assessment

1. The client requests an assessment for a resident and assistance program.
2. Django retrieves the relevant resident facts and program rules.
3. The deterministic eligibility engine evaluates each criterion.
4. Each criterion receives `Met`, `Unmet`, or `Unknown`.
5. Django creates an immutable assessment snapshot.
6. The API returns the assessment result and criterion explanations.

AI output must not alter the deterministic result.

### Program Matching

1. The client requests relevant assistance programs.
2. Django retrieves active and published program records.
3. The matching workflow applies applicable filters and eligibility information.
4. Where semantic retrieval is needed, Django requests AI-service support.
5. The AI service returns retrieval or reranking results.
6. Django validates the returned references against authoritative program records.
7. The client receives program matches and their explanations.

Semantic relevance is not proof of eligibility.

### Document Processing

1. The client uploads a document through an authorized backend endpoint.
2. Django validates the file and stores it in object storage.
3. Django creates document metadata.
4. Django queues an OCR task through Celery.
5. A worker processes the document using Tesseract.
6. Extracted text and processing metadata are stored.
7. Validation checks completeness, readability, and consistency against applicable requirements.
8. Authorized reviewers can inspect and act on the document.

OCR output is not automatically considered verified information.

## 4. Data Ownership

- Django owns authoritative business records.
- PostgreSQL is the system of record.
- pgvector stores derived vector representations.
- Redis stores transient task and cache-related data.
- Object storage holds uploaded files.
- The AI service produces derived outputs and does not own final business decisions.

## 5. Reliability and Failure Handling

- AI service failures must not corrupt program or application records.
- A failed background task must be observable and eligible for controlled retry.
- Duplicate task execution must not create duplicate business records.
- Document processing failures must be visible to authorized users.
- Program embedding failures must not prevent the underlying program record from being saved.
- API operations that create important records should use appropriate database transactions.
- External model calls should have timeouts and controlled error handling.

## 6. Security Boundaries

- Public clients communicate with the public API.
- Internal AI endpoints are not exposed as public client APIs.
- Database and Redis credentials remain server-side.
- Object storage access is mediated by backend authorization.
- Administrative operations require explicit permissions.
- Sensitive operations should produce audit records.

## 7. Architectural Constraints

1. Do not place business logic in React components.
2. Do not let mobile and web clients implement separate eligibility rules.
3. Do not let AI replace deterministic eligibility evaluation.
4. Do not let AI directly approve applications.
5. Do not let clients access internal infrastructure directly.
6. Avoid circular dependencies between Django applications.
7. Keep asynchronous work outside latency-sensitive request paths where practical.
8. Preserve assessment history when program rules change.