# Dependency and Credentials Checklist

This checklist tracks every dependency, binary, credential, and API key that
QUALIFIL needs but is **not** already provided by the repository or installed on
the development machine. Use it before starting the local stack and again before
starting each sprint that introduces a new external dependency.

Legend:

- `[ ]` Not provided yet
- `[x]` Provided and verified
- **Owner** — who must supply the item:
  - **You** — download, account, binary, secret, or credentials only you can provide.
  - **Agent** — an AI coding agent can install or scaffold it in the repo.

> Never commit `.env`, API keys, passwords, model cache folders, or uploaded
> documents. Only `.env.example` belongs in Git.

## Current Machine Snapshot

Verified on 2026-11-28 for the repository at `qualifil-core/`.

| Item | Status | Notes |
|---|---|---|
| Node.js `>=22` | Installed (v22.23.2) | Satisfies root `engines` requirement. |
| npm `>=10` | Installed (10.9.8) | |
| npm workspace dependencies | Installed | Root, `web/`, `mobile/`, `packages/api-client`. |
| `packages/api-client/dist` | Built | Rebuild after client changes. |
| Python `3.12+` | Installed (3.13.2) | Project containers/CI use 3.12; see Python note below. |
| Backend Python dependencies | Installed | `backend/requirements/dev.txt` satisfied. |
| AI service Python dependencies | Installed | `ai-service/requirements-dev.txt` satisfied. |
| Git | Installed | |
| Docker Desktop | **Missing** | Required for the documented PostgreSQL 18 + pgvector and Redis services. |
| PostgreSQL | Local 17 service running | Project targets PostgreSQL **18 + pgvector**; local 17 has no `vector` extension. |
| pgvector extension | **Missing** | `vector.control` not present in the local PostgreSQL 17 install. |
| Redis | **Missing** | No `redis-server`, Memurai, or Redis service installed. |
| `.env` | **Missing** | Only `.env.example` exists. |
| Tesseract OCR | **Missing** | Needed from Sprint 04B onward. |
| Anthropic SDK / API key | **Missing** | Needed from Sprint 03G onward. |
| ML libraries (`sentence-transformers`, `transformers`) | **Missing** | `torch` and `numpy` are already installed. Needed from Sprint 03D onward. |
| Qwen model weights | **Missing** | No Hugging Face cache. Needed from Sprint 03D onward. |
| `pgvector` Python package | **Missing** | Needed from Sprint 03E onward. |
| Expo Go / emulator | **Missing** | `adb` and `emulator` are not on `PATH`. Needed to run the mobile app on a device. |

## 1. Required Now — Host Tooling

- [ ] **Docker Desktop** — Owner: **You**
  - Install: `winget install -e --id Docker.DockerDesktop`
  - Restart the machine or sign out/in so `docker` is on `PATH`.
  - Verify: `docker --version` and `docker compose version`.
  - Start Docker Desktop before running any Compose command.

- [ ] **Python 3.12 virtual environment (recommended)** — Owner: **You**
  - The installed Python 3.13 runs the current foundation, but CI and Docker pin
    Python 3.12, and the Sprint 03D ML stack has the widest wheel support on 3.12.
  - If Python 3.12 is not installed: `winget install -e --id Python.Python.3.12`
  - Create and activate from the repository root:
    ```powershell
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    ```

- [x] **Node.js 22+ and npm 10+** — already installed.
- [x] **Git** — already installed.

## 2. Required Now — Infrastructure

The repository's supported path is Docker Compose, which supplies the exact
PostgreSQL 18 + pgvector and Redis versions used by CI.

- [ ] **Create `.env` before starting Compose** — Owner: **You**
  - `backend/docker-compose.yml` reads `../.env`, so this must exist first.
  - From the repository root:
    ```powershell
    Copy-Item .env.example .env
    ```

- [ ] **PostgreSQL 18 + pgvector** — Owner: **You** (Docker install) / **Agent** (commands)
  - From the repository root:
    ```powershell
    docker compose -f backend/docker-compose.yml up -d db
    ```
  - The `pgvector/pgvector:pg18` image and `backend/docker/init.sql` create the
    `vector` extension automatically on first initialization.
  - Verify:
    ```powershell
    docker compose -f backend/docker-compose.yml exec db psql -U qualifil -d qualifil -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
    ```

- [ ] **Redis 7** — Owner: **You** (Docker install) / **Agent** (commands)
  - ```powershell
  docker compose -f backend/docker-compose.yml up -d redis
  ```
  - Verify: `docker compose -f backend/docker-compose.yml exec redis redis-cli ping`
    (expected `PONG`).

- [ ] **Local database role and schema** — Owner: **You** / **Agent**
  - The Compose service creates database `qualifil` with user `qualifil` and the
    password from `.env`.
  - Apply migrations after the database is healthy:
    ```powershell
    python backend/manage.py migrate
    ```

### Native alternative (no Docker)

Only use this if Docker cannot be installed. The supported path remains Compose.

- **PostgreSQL 18 + pgvector**: install PostgreSQL 18, then install pgvector for
  that installation (Windows builds are not bundled and usually require Visual
  Studio Build Tools plus `nmake`, or a prebuilt distribution). Then run
  `CREATE EXTENSION IF NOT EXISTS vector;` in the `qualifil` database.
- **Redis on Windows**: install Memurai (Redis-compatible) or run Redis 7 inside
  WSL. Point `REDIS_URL`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` at it.

## 3. Required Now — Environment Variables and Secrets

Copy `.env.example` to `.env`, then fill each item below. Real environment
variables always override `.env`, so container and CI values are never replaced.

- [ ] `DJANGO_SECRET_KEY` — Owner: **You** (generate)
  ```powershell
  python -c "import secrets; print(secrets.token_urlsafe(48))"
  ```
- [ ] `POSTGRES_PASSWORD` — Owner: **You** (choose a local password)
- [ ] `DATABASE_URL` — Owner: **You**
  - Must use the same password, host, port, and database name as `POSTGRES_*`:
    `postgresql://qualifil:<password>@localhost:5432/qualifil`
- [ ] `AI_SERVICE_API_KEY` — Owner: **You** (generate)
  - Shared secret sent as the `X-Internal-API-Key` header between Django and the
    AI service.
  - Generate another value with the `secrets.token_urlsafe(48)` command above.
- [ ] `EXPO_PUBLIC_API_BASE_URL` — Owner: **You**
  - Physical device: use the computer's LAN IP, for example
    `http://192.168.1.10:8000` (not `localhost`).
  - Emulator/simulator: `http://localhost:8000` is usually fine.
- [ ] `VITE_API_BASE_URL` — Owner: **You**
  - Leave empty during development to use the Vite proxy.
- [ ] `DJANGO_CORS_ALLOWED_ORIGINS` — Owner: **You**
  - Defaults to `http://localhost:5173,http://localhost:8081`.
- [ ] `LLM_MODEL` — Owner: **You** (confirm)
  - `.env.example` currently uses the placeholder label `claude-haiku-5-5`.
    Replace it with the exact provider model ID when the Anthropic key is issued.

Security rules:

- Do not put secrets in `VITE_*` or `EXPO_PUBLIC_*`; both are exposed to clients.
- Do not commit `.env`. Confirm `git status` does not list it.
- Use unique local values; do not reuse production credentials.

## 4. Required Now — Mobile Device or Simulator

- [ ] **Expo Go** on a physical Android/iOS device — Owner: **You**
  - Install from the app store, then scan the QR code from
    `npm run start -w qualifil-mobile`.
- [ ] **or** an Android emulator / iOS simulator — Owner: **You**
  - Android: install Android Studio, create a virtual device, and put
    `platform-tools` (`adb`) and `emulator` on `PATH`.
  - iOS: use Xcode on macOS.

## 5. Required Before Later Sprints

These are not needed for the v0.1.0 foundation but will block their sprints if
not provisioned in advance.

| Sprint | Dependency | Owner | Action |
|---|---|---|---|
| 03D | `sentence-transformers`, `transformers`, `huggingface-hub` | Agent | Add to `ai-service/requirements.txt`; `torch` is already installed. |
| 03D | `Qwen/Qwen3-Embedding-0.6B` weights | **You** | Accept the model terms if required, then download; expect several GB of disk. |
| 03D | `Qwen/Qwen3-Reranker-0.6B` weights | **You** | Same as above. |
| 03D | Embedding/reranker compute | **You** | CPU inference is acceptable for development; benchmark before relying on it. |
| 03E | Python `pgvector>=0.3` | Agent | Add to `backend/requirements/base.txt`. |
| 03G | Anthropic API key | **You** | Create a key in the Anthropic console and set `ANTHROPIC_API_KEY`. |
| 03G | `anthropic` Python SDK | Agent | Add to `ai-service/requirements.txt`. |
| 04A | S3-compatible storage | **You** | Provide real S3 credentials, or run MinIO locally. |
| 04B | Tesseract OCR binary | **You** | `winget install -e --id UB-Mannheim.TesseractOCR` |
| 04B | Tesseract language data (`eng`, `fil`) | **You** | Install/copy `eng.traineddata` and `fil.traineddata` into the Tesseract `tessdata` folder. |
| 04B | `pytesseract`, `Pillow`, PDF renderer | Agent | Add to backend requirements; `Pillow` is already installed. |
| 04B | Poppler (for `pdf2image`) or `pymupdf` | **You** / Agent | Install Poppler and add `bin` to `PATH`, or use `pymupdf` as the renderer. |

### Downloading the Qwen models

```powershell
python -m pip install huggingface_hub
huggingface-cli download Qwen/Qwen3-Embedding-0.6B
huggingface-cli download Qwen/Qwen3-Reranker-0.6B
```

Set `HF_HOME` to a drive with enough free space if the default user cache is too
small. The AI service reads the model names from `EMBEDDING_MODEL` and
`RERANKER_MODEL`.

### Tesseract on Windows

- The default `.env.example` value `TESSERACT_CMD=/usr/bin/tesseract` is a Linux
  path. On Windows set it to the installed executable, for example:
  `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`
- Mirror the language data installed locally in `OCR_DEFAULT_LANGUAGE` and
  `OCR_ADDITIONAL_LANGUAGES`.

### Local S3-compatible storage (MinIO)

If real S3 credentials are not available for development, run MinIO and set
`S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, and `S3_SECRET_ACCESS_KEY` accordingly:

```powershell
docker run -d --name qualifil-minio -p 9000:9000 -p 9001:9001 `
  -e MINIO_ROOT_USER=qualifil -e MINIO_ROOT_PASSWORD=<local-password> `
  -v qualifil_minio:/data minio/minio server /data --console-address ":9001"
```

Create the `qualifil-documents` bucket in the MinIO console at
`http://localhost:9001` before uploading documents.

## 6. Verification

Run from the repository root after the checklist is complete.

```powershell
# Tooling
node -v
npm -v
python --version
docker --version

# Infrastructure
docker compose -f backend/docker-compose.yml ps
docker compose -f backend/docker-compose.yml exec redis redis-cli ping

# Backend
python -m pip install -r backend/requirements/dev.txt
python backend/manage.py check
python backend/manage.py migrate

# AI service
python -m pip install -r ai-service/requirements-dev.txt
uvicorn app.main:app --app-dir ai-service --port 8001

# Tests
python -m pytest
npm run build -w @qualifil/api-client
npm run build -w qualifil-web
npm run lint -w qualifil-web
npm test -w qualifil-web -- --run
npm run typecheck -w qualifil-mobile
npm test -w qualifil-mobile -- --watchAll=false --runInBand
```

Expected results:

- `manage.py check` reports no `pgvector` error when the Compose database is up.
- `redis-cli ping` returns `PONG`.
- `python -m pytest` runs both the backend and AI service suites.
- The web build and all lint/test commands exit successfully.

## 7. Related Documentation

- [`LOCAL_DEVELOPMENT.md`](LOCAL_DEVELOPMENT.md) — step-by-step local setup.
- [`../../.env.example`](../../.env.example) — full environment variable template.
- [`../api/AI_SERVICE.md`](../api/AI_SERVICE.md) — AI service configuration keys.
- [`../security/SECURITY.md`](../security/SECURITY.md) — secret handling requirements.
