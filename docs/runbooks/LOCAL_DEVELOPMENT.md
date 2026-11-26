# Local Development Runbook

This runbook describes how to run the QUALIFIL backend, AI service, web app, and
mobile app on a development machine.

## Prerequisites

- Python 3.12 or newer
- Node.js 22 or newer and npm 10 or newer
- Docker Desktop (optional, recommended for PostgreSQL/Redis)
- Expo Go on a physical device, or an Android/iOS simulator

## 1. Environment Variables

The repository uses a single shared `.env` file at the repository root. The
backend, AI service, Vite, and Expo all read it.

```sh
cp .env.example .env
```

Required local values:

- `POSTGRES_PASSWORD` — database password used by Docker Compose.
- `DJANGO_SECRET_KEY` — any long random string for local development.
- `EXPO_PUBLIC_API_BASE_URL` — backend origin reachable from the device.
  On a physical device use your computer's LAN IP, for example
  `http://192.168.1.10:8000`. `localhost` only works on the same machine or a
  simulator.
- `VITE_API_BASE_URL` — leave empty during development so the Vite proxy keeps
  browser requests same-origin. Set a full origin for production builds.
- `DJANGO_CORS_ALLOWED_ORIGINS` — comma-separated additional browser origins
  (defaults to `http://localhost:5173,http://localhost:8081`).

Real environment variables always take precedence over `.env`, so container and
CI values are never overwritten.

## 2. Infrastructure

```sh
cd backend
docker compose up -d db redis
cd ..
```

This starts PostgreSQL 18 with pgvector and Redis. The database runs the
`pgvector` extension initialization script on first start.

## 3. Backend

```sh
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r backend/requirements/dev.txt
python backend/manage.py migrate
python backend/manage.py runserver
```

The API is available at `http://localhost:8000/api/v1/`.

`python backend/manage.py check` reports an `api.W001` warning when PostgreSQL
is unreachable. This is expected before infrastructure is started. The
database test suite skips that one connectivity test when PostgreSQL is not
available instead of failing.

## 4. AI Service

```sh
pip install -r ai-service/requirements-dev.txt
uvicorn app.main:app --app-dir ai-service --port 8001
```

The service listens on `http://localhost:8001` and requires the internal API
key for internal endpoints.

## 5. Web Application

Install workspace dependencies once from the repository root:

```sh
npm install
```

Then run:

```sh
npm run dev -w qualifil-web
```

The web app is available at `http://localhost:5173`. Requests to `/api` are
proxied to `http://localhost:8000` by Vite during development.

## 6. Mobile Application

```sh
npm install
npm run start -w qualifil-mobile
```

Open the app with Expo Go or a simulator. Set `EXPO_PUBLIC_API_BASE_URL` to a
backend origin the device can reach.

The mobile app is an npm workspace, so always install from the repository root
to keep `@qualifil/api-client` linked.

## 7. Shared API Client

`packages/api-client` is the single HTTP client used by web and mobile. It is
built to `packages/api-client/dist` because Metro resolves the package through
its build output.

```sh
npm run build -w @qualifil/api-client
```

The root `prepare` script builds it automatically after `npm install`/`npm ci`.

## 8. Tests and Quality Checks

```sh
# Backend
python -m pytest backend

# AI service
python -m pytest ai-service

# Shared client
npm test -w @qualifil/api-client

# Web
npm test -w qualifil-web -- --run
npm run build -w qualifil-web
npm run lint -w qualifil-web

# Mobile
npm test -w qualifil-mobile -- --watchAll=false --runInBand
npm run typecheck -w qualifil-mobile
npm run lint -w qualifil-mobile
```

Formatting is handled by Prettier:

```sh
npm run format
npm run format:check
```

## Troubleshooting

- **`fe_sendauth: no password supplied`** — PostgreSQL is running but
  `POSTGRES_PASSWORD`/`DATABASE_URL` do not match an existing role. Start the
  Compose database or correct `.env`.
- **App cannot reach the backend on a phone** — use the computer's LAN IP for
  `EXPO_PUBLIC_API_BASE_URL`, allow the port through the firewall, and ensure
  both devices are on the same network.
- **Browser CORS errors** — during development use the Vite proxy (leave
  `VITE_API_BASE_URL` empty) or add the exact origin to
  `DJANGO_CORS_ALLOWED_ORIGINS`.
- **Metro cannot resolve `@qualifil/api-client`** — run `npm install` from the
  repository root and rebuild the shared client.
