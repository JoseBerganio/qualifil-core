# QUALIFIL AI Service — Internal API Contract

- Sprint introduced: 01C — AI Service Foundation
- Service: `ai-service` (FastAPI)
- Default base URL: `http://localhost:8001`
- Consumers: Django backend only

The AI service produces derived outputs. It does not own authoritative business
records and must never make final eligibility, approval, or selection decisions.
Web and mobile clients must not call this service directly.

Model loading and inference are deferred to v0.3.0. During the foundation
release the service exposes health, authentication, and model-status behavior
only.

## 1. Authentication

Health endpoints are public so container orchestrators can probe them.

Every other endpoint requires the internal service key:

```http
X-Internal-API-Key: <AI_SERVICE_API_KEY>
```

- Missing key: `401 UNAUTHENTICATED`
- Invalid key: `403 FORBIDDEN`

Keys are compared in constant time. The backend must keep the key server-side
and send it only from trusted service code.

## 2. Request IDs

Every response includes `X-Request-ID`. If the caller supplies the header, the
service reuses it; otherwise it generates one. The value is included in
structured request logs so backend and AI service records can be correlated.

## 3. Endpoints

### `GET /health/live`

Public liveness check. Requires no external services.

```json
{
  "status": "ok",
  "service": "ai-service",
  "environment": "development",
  "version": "0.1.0"
}
```

### `GET /health/ready`

Public readiness check. Returns `200` when ready and `503` when degraded.

```json
{
  "status": "ok",
  "checks": {
    "service": true,
    "configuration": true,
    "providers": true
  }
}
```

Models are expected to be unloaded until Sprint 03D; model readiness is not
required for the foundation release.

### `GET /internal/v1/models/status`

Requires `X-Internal-API-Key`. Reports the configured models and their current
lifecycle state without loading them.

```json
{
  "status": "ok",
  "models": [
    {
      "role": "embedding",
      "name": "Qwen/Qwen3-Embedding-0.6B",
      "device": "cpu",
      "revision": null,
      "status": "not_loaded"
    },
    {
      "role": "reranker",
      "name": "Qwen/Qwen3-Reranker-0.6B",
      "device": "cpu",
      "revision": null,
      "status": "not_loaded"
    },
    {
      "role": "explanation",
      "name": "claude-haiku-5-5",
      "device": null,
      "revision": null,
      "status": "not_loaded"
    }
  ]
}
```

`status` is one of `not_loaded`, `loading`, `ready`, or `unavailable`.

## 4. Standardized Errors

Errors use the same envelope as the Django backend:

```json
{
  "error": {
    "code": "UNPROCESSABLE_ENTITY",
    "message": "Request validation failed.",
    "status": 422,
    "details": [
      {
        "field": "query",
        "message": "Field required."
      }
    ]
  }
}
```

`details` is optional. Unknown fields in a request body are rejected so contract
drift fails at the boundary instead of being ignored.

## 5. Configuration

The service reads the shared root `.env` file. Relevant variables:

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `development` | Runtime environment; controls docs exposure and key requirements |
| `APP_VERSION` | `0.1.0` | Reported service version |
| `APP_DEBUG` | `false` | Debug flag |
| `AI_SERVICE_HOST` | `0.0.0.0` | Bind host |
| `AI_SERVICE_PORT` | `8001` | Bind port |
| `AI_SERVICE_API_KEY` | development-only fallback | Shared internal service key |
| `AI_SERVICE_TIMEOUT_SECONDS` | `60` | Outbound request timeout budget |
| `LOG_LEVEL` | `INFO` | Log level |
| `EMBEDDING_MODEL` | `Qwen/Qwen3-Embedding-0.6B` | Configured embedding model |
| `EMBEDDING_DEVICE` | `cpu` | Embedding device |
| `RERANKER_MODEL` | `Qwen/Qwen3-Reranker-0.6B` | Configured reranker model |
| `RERANKER_DEVICE` | `cpu` | Reranker device |
| `LLM_PROVIDER` | `anthropic` | Explanation provider |
| `LLM_MODEL` | `claude-haiku-5-5` | Explanation model label |

Outside development (`APP_ENV` not in `development`, `local`, `test`,
`testing`), `AI_SERVICE_API_KEY` is required and service documentation
endpoints are disabled.

## 6. Local Development

```bash
cd ai-service
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --port 8001
```

Interactive docs are available at `http://localhost:8001/docs` outside
production.

## 7. Docker

The AI service is part of the development stack defined in
`backend/docker-compose.yml`:

```bash
cd backend
docker compose up -d ai
```

The container listens on `${AI_SERVICE_PORT:-8001}` and health-checks
`/health/live`.

## 8. Testing

```bash
cd ai-service
python -m pytest -q
```

CI installs `ai-service/requirements-dev.txt` and runs the suite from the
`ai-service` directory. Tests use FastAPI's test client and do not require a
model runtime, GPU, external provider key, or network access.
