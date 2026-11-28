# QUALIFIL — Authentication API Contract (v0.2.0 / Sprint 02A)

All endpoints are mounted under `/api/v1/auth/`. Errors use the standard QUALIFIL envelope described in [the backend error module](../../backend/api/errors.py).

## 1. Client transports

Two transports are supported and selected explicitly with the `X-Auth-Mode` request header (`bearer` by default):

| Mode | Client | Tokens | CSRF |
|---|---|---|---|
| `bearer` | Mobile / native and generic API clients | JSON `access` and `refresh`; sent as `Authorization: Bearer <access>` | Not required |
| `cookie` | Web browser | httpOnly cookies `qualifil_access` / `qualifil_refresh` (`SameSite=Lax`, `Secure` when `JWT_COOKIE_SECURE=true`) | Required for unsafe methods |

The web client must first call `GET /api/v1/auth/csrf/` to obtain the readable `csrftoken` cookie and `csrfToken` value. Every subsequent unsafe request (`POST`, `PUT`, `PATCH`, `DELETE`) must send that value in the `X-CSRFToken` header. The shared `@qualifil/api-client` handles this automatically in cookie mode.

JWTs are never stored in `localStorage`. Native mobile tokens are stored with `expo-secure-store` behind `mobile/src/lib/storage/tokenStorage.ts`.

## 2. Endpoints

### `POST /api/v1/auth/register/`

Public. Creates a `RESIDENT` account only. Staff/admin roles supplied by a client are ignored.

Request:

```json
{
  "email": "resident@example.test",
  "password": "<validated password>",
  "first_name": "Synthetic",
  "last_name": "Resident",
  "phone_number": "09000000000"
}
```

Behavior: validates password using Django's `AUTH_PASSWORD_VALIDATORS`, normalizes the email to lowercase, and rejects duplicate emails (case-insensitively) with `409 CONFLICT`.

Response: `201 CREATED`. In bearer mode it contains `access`, `refresh`, and `user`; in cookie mode it contains only `user` and sets the two httpOnly cookies.

### `POST /api/v1/auth/login/`

Public. Verifies credentials and returns a token pair.

Request: `{ "email": "...", "password": "..." }`.

Invalid credentials, unknown emails, and inactive accounts all return the same `401 UNAUTHENTICATED` message so the endpoint does not disclose whether an email is registered.

After `AUTH_MAX_FAILED_LOGIN_ATTEMPTS` (default 5) consecutive failures, the account is locked for `AUTH_LOCKOUT_MINUTES` (default 15). Locked accounts receive `429 TOO_MANY_REQUESTS` until the lock expires; a successful login resets the counter.

### `POST /api/v1/auth/refresh/`

Public. In bearer mode the refresh token is sent in the JSON body (`{"refresh": "..."}`); in cookie mode it is read from the `qualifil_refresh` cookie.

Tokens rotate on every refresh: the old refresh token is blacklisted and a new one is issued (configurable through `SIMPLE_JWT`). A revoked, expired, or malformed token returns `401 UNAUTHENTICATED`.

### `POST /api/v1/auth/logout/`

Blacklists the refresh token from the body or cookie. The operation is idempotent. In cookie mode it also clears both auth cookies. Returns `204 NO CONTENT`.

### `GET /api/v1/auth/me/`

Requires authentication. Returns the current user's summary:

```json
{
  "id": "<uuid>",
  "email": "resident@example.test",
  "phone_number": "",
  "first_name": "",
  "last_name": "",
  "full_name": "",
  "role": "RESIDENT",
  "memberships": [],
  "is_active": true,
  "is_staff": false,
  "created_at": "2026-11-28T00:00:00Z"
}
```

Active staff `OrganizationMembership` objects are returned in `memberships` (introduced in Sprint 02B; see [ORGANIZATIONS.md](ORGANIZATIONS.md)).

### `POST /api/v1/auth/change-password/`

Requires authentication. Request: `{ "current_password": "...", "new_password": "..." }`. Validates the new password, updates the hash, and blacklists all outstanding refresh tokens for the user. Returns `204 NO CONTENT`; clients should log in again with the new password.

### `GET /api/v1/auth/csrf/`

Public. Sets the readable `csrftoken` cookie and returns `{ "csrfToken": "..." }`. Used only by the cookie transport.

### Throttling

`login`, `register`, and `refresh` use DRF `ScopedRateThrottle` with configurable rates (`AUTH_LOGIN_THROTTLE_RATE`, `AUTH_REGISTER_THROTTLE_RATE`, `AUTH_REFRESH_THROTTLE_RATE`). Exceeding a rate returns `429 TOO_MANY_REQUESTS`.

## 3. Shared client usage

```ts
import { createApiClient } from "@qualifil/api-client";

// Mobile / native
const mobileClient = createApiClient({
  baseUrl: "https://api.example.test",
  authMode: "bearer",
  getAccessToken: () => tokenStorage.getAccessToken(),
  getRefreshToken: () => tokenStorage.getRefreshToken(),
  setTokens: (tokens) => tokenStorage.setTokens(tokens),
  clearTokens: () => tokenStorage.clear(),
});

// Web browser
const webClient = createApiClient({ baseUrl: "", authMode: "cookie", credentials: "include" });

await webClient.auth.login({ email, password });
const me = await webClient.auth.getMe();
```

The client retries a failed request once after refreshing an expired token, and skips refresh for the auth endpoints themselves.

## 4. Environment variables

See `.env.example` for `JWT_*`, `AUTH_*` throttle/lockout, `DJANGO_CORS_ALLOW_CREDENTIALS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, and cookie settings.

## 5. Scope note

Sprint 02A creates authentication accounts only; resident profiles, consent, and barangay approval arrive in Sprint 02D. Organization roles and scoping arrive in Sprint 02B.
