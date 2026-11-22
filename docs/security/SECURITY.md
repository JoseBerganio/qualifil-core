# QUALIFIL — Security Guidelines

## 1. Purpose

This document defines baseline security expectations for development and deployment.

The system handles resident information and uploaded documents. Access must be limited to authorized users and legitimate organizational responsibilities.

## 2. Authentication

- Use the approved authentication mechanism.
- Protect account credentials.
- Use secure password handling provided by Django.
- Configure JWT lifetimes deliberately.
- Reject invalid, expired, and revoked tokens where applicable.
- Do not store credentials in source code.

## 3. Authorization

- Enforce permissions on the backend.
- Do not rely on hidden frontend buttons as an authorization mechanism.
- Enforce organization-level data boundaries.
- Verify that barangay personnel can access only records permitted by their assignment.
- Restrict LGU administrative operations to authorized roles.
- Test both allowed and denied access paths.

## 4. Resident Information

- Collect only information required for defined system functions.
- Avoid unnecessary exposure of resident information in API responses.
- Avoid logging sensitive personal information.
- Use synthetic data in development and automated tests.
- Restrict access to resident records and uploaded documents.
- Establish appropriate retention and deletion policies before production deployment.

## 5. File Upload Security

- Enforce file size limits.
- Restrict allowed file extensions and actual file formats.
- Generate safe storage names.
- Do not trust client-supplied filenames or MIME types.
- Prevent uploaded files from being served as executable content.
- Restrict document access through backend authorization.
- Consider malware scanning before production use.

## 6. AI Service Security

- Keep model-provider credentials server-side.
- Authenticate internal service requests.
- Apply request timeouts and input limits.
- Avoid sending unnecessary personal information to external model providers.
- Define what data may be sent to each provider.
- Treat model responses as untrusted input.
- Validate model output before using it.
- Prevent model output from directly changing eligibility or approval decisions.

## 7. Infrastructure

- Do not expose PostgreSQL or Redis publicly without an explicit secured operational requirement.
- Use separate credentials for development, testing, and production.
- Use TLS for production service communication.
- Restrict object storage access.
- Rotate credentials when exposure is suspected.
- Apply security updates to dependencies and base images.

## 8. Audit Logging

Record important actions such as:
- Administrative changes
- Program publication and rule changes
- Application review actions
- Applicant selection decisions
- Distribution updates
- Permission changes
- Sensitive record access where required by policy

Audit logs should identify the actor, action, target record, timestamp, and relevant context without unnecessarily copying sensitive data.

## 9. Incident Handling

When a security issue is suspected:
1. Record the incident and time discovered.
2. Notify the designated project or system administrator.
3. Restrict affected credentials or access where necessary.
4. Preserve relevant logs and evidence.
5. Determine affected records and services.
6. Apply and test a corrective action.
7. Document the incident and preventive measures.

## 10. Production Readiness

Before production deployment, review:
- Authentication and authorization
- Organization-level access restrictions
- File upload controls
- Secret management
- Database backups
- Object storage permissions
- Logging and monitoring
- Dependency vulnerabilities
- AI data-sharing practices
- Privacy and retention requirements

This document is an engineering baseline, not a substitute for legal, privacy, or organizational approval.