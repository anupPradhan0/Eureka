# Eureka — backend

FastAPI service for Eureka, organized as a strict layered architecture.

## Architecture

```
Request
   ↓
Routes        (src/routes)         — HTTP endpoints, wiring/DI
   ↓
Controller    (src/controllers)    — request/response handling
   ↓
Service       (src/services)       — business logic
   ↓
Repository    (src/repositories)   — data access (interface + Mongo impl)
   ↓
MongoDB Model (src/models)         — entities / documents
```

Each layer only talks to the layer directly below it. Repositories are accessed
through interfaces (`repositories/interfaces`) so services depend on abstractions,
not concrete database code (Dependency Inversion).

## Layout

```
src/
├── app.py                  # FastAPI entry point (router registration, lifespan, CORS)
├── config/                 # settings + MongoDB connection
├── routes/                 # route definitions (auth, ai-config, repository, health)
├── controllers/            # HTTP request/response handling
├── services/               # business logic
├── repositories/
│   ├── interfaces/         # abstractions (one per aggregate)
│   ├── base_repository.py  # generic CRUD
│   └── *_repository.py     # concrete Mongo implementations
├── providers/              # outbound integrations
│   ├── ai/                 # BYO AI providers (anthropic/openai/openrouter/gemini) + registry
│   └── github/             # GitHub API client + SSRF-guarded URL parser
├── models/                 # DB entities
├── schemas/                # pydantic request/response DTOs
├── core/                   # security, crypto, exceptions, utils
└── dependencies/           # DI wiring (incl. the shared httpx client)
```

## API

All routes are under `/api`, JSON, and require a Bearer token except where noted.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness (no auth) |
| POST | `/api/auth/register` | Create account, returns a token |
| POST | `/api/auth/login` | Authenticate, returns a token |
| GET | `/api/auth/me` | Current user |
| GET | `/api/ai-config` | AI config status (never returns the key) |
| PUT | `/api/ai-config` | Validate the key live, then save provider/model/key |
| GET | `/api/repository` | Current imported repo summary (404 if none) |
| POST | `/api/repository/import` | Fetch + persist a repo summary |
| POST | `/api/repository/refresh` | Re-fetch the current repo |
| DELETE | `/api/repository` | Clear the current repo |

## Configuration

Settings load from `.env` (copy `.env.example`). Key variables:

- `MONGODB_URI`, `MONGODB_DB_NAME`
- `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRES_MINUTES`
- `ENCRYPTION_KEY` — Fernet key encrypting BYO API keys / GitHub tokens at rest
- `ALLOWED_ORIGINS` — comma-separated CORS origins
- `AI_HTTP_TIMEOUT_SECONDS`, `GITHUB_HTTP_TIMEOUT_SECONDS`, `GITHUB_TREE_MAX_ENTRIES`, `README_MAX_CHARS`

In `APP_ENV=production` the app refuses to start while `ENCRYPTION_KEY` or
`JWT_SECRET` are left at their dev defaults. Secrets are encrypted at rest and
never returned to clients — responses carry only a masked hint (e.g. `••••1234`).

## Setup

The backend is Python; it is not managed by pnpm (pnpm is used for the frontend).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env        # then edit values
```

## Run

```bash
uvicorn src.app:app --reload
```

Then open:
- Health check: http://localhost:8000/api/health
- API docs: http://localhost:8000/docs

## Test

```bash
pytest
```

Tests use an in-memory Mongo (`mongomock-motor`), so no running database is needed.
