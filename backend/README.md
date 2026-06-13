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
├── app.py                  # FastAPI entry point
├── config/                 # settings + MongoDB connection
├── routes/                 # route definitions
├── controllers/            # HTTP request/response handling
├── services/               # business logic
├── repositories/
│   ├── interfaces/         # abstractions
│   ├── base_repository.py  # generic CRUD
│   └── user_repository.py  # concrete Mongo implementation
├── models/                 # DB entities
├── schemas/                # pydantic request/response DTOs
├── core/                   # security, exceptions
└── dependencies/           # dependency injection wiring
```

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
