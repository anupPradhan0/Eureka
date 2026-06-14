# Eureka

**Low-code, built _into_ your self-hosted open-source apps.**

Eureka is an installable add-on for self-hosted open-source projects. You deploy
your own copy of an open-source product, drop Eureka inside it, log in, point at a
page, and describe the feature you want in plain language — Eureka's agent builds it
into your instance. No fork, no patches to maintain, no coding required.

## Why

Low-code today is great at building *new* apps. The gap is adding low-code *into*
existing, mature products. Self-hosters constantly want tweaks specific to their own
deployment but don't have the skills or time to implement them. Eureka turns
"I wish my instance could do X" into a working feature.

## How it works

1. Self-host an open-source project (the "foundation project").
2. Install Eureka inside it as an add-on.
3. Log in to Eureka's UI (email + password).
4. Point at the page / part you want to change.
5. Describe the feature you want.
6. The Eureka agent builds it into your deployment.

## What works today

The onboarding flow is implemented end-to-end (the agent that actually builds
features is still TBD). After logging in, a user is guided through three gated
steps:

1. **Configure an AI model (bring your own key).** Eureka ships no AI access of
   its own — you pick a provider (**Anthropic, OpenAI, OpenRouter, or Google
   Gemini**), a model, and an API key. The key is validated live against the
   provider, encrypted at rest, and never returned to the browser.
2. **Import a repository.** Paste the GitHub URL of the project you'll build into
   (optionally with a token for private repos / higher rate limits).
3. **Review the summary.** Eureka shows the project's description, stars,
   contributor count, file count, full file tree, and documentation files
   (README, Code of Conduct, Contributing, License, Security) with the README
   shown. Stats GitHub can't provide are simply hidden.

The imported repo is remembered between sessions (refresh to re-fetch, or import
a different one).

## Tech stack

- **Frontend:** Vite + React + TypeScript + TanStack Query
- **Backend:** FastAPI (Python) + MongoDB
- **AI:** bring-your-own-key — Anthropic / OpenAI / OpenRouter / Gemini
- **Agent:** TBD

## Status

Early / scaffolding. Phase 1 focuses on **self-hosted** deployments; project-wide
rollout for maintainers is deferred to a later phase.

## Docs

- [Vision](./docs/vision.md) — product vision, user flow, open questions
- [Tech Stack & Next Steps](./docs/tech-stack.md) — stack and what's still undecided

## Repository layout

```
backend/            FastAPI app (routes → controllers → services → repositories → models)
frontend/           Vite + React + TypeScript app
docs/               vision and tech-stack docs
.claude/            project agents + skills (e.g. the /sonnet-review code-review skill)
docker-compose.yml  dev stack (backend + frontend + MongoDB) with hot reload
```

## Development (Docker, hot reload)

The whole stack runs in Docker with live reload — edit files on your host and
the containers pick up changes automatically.

```bash
docker compose up --build
```

- Frontend (Vite + HMR): http://localhost:5173
- Backend (FastAPI + uvicorn --reload): http://localhost:8000 — docs at `/docs`
- MongoDB: localhost:27017

Source folders are bind-mounted; `node_modules` and the Python install live in
the images / named volumes so the host can't shadow them. Stop with
`docker compose down` (add `-v` to also drop the Mongo data volume).

Prefer running without Docker? See `backend/README.md` and `frontend/README.md`.

## Configuration

Backend settings live in `backend/.env` (copy from `backend/.env.example`). Two
secrets must be set to real values before any production deployment — the app
**refuses to boot in `APP_ENV=production`** while they're left at the dev defaults:

- `ENCRYPTION_KEY` — Fernet key protecting stored API keys / GitHub tokens.
  Generate with
  `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
- `JWT_SECRET` — signing secret for auth tokens.

`ALLOWED_ORIGINS` (comma-separated) sets the CORS origins for non-dev frontends.
Full list of variables is in `backend/README.md`.

## Code review

`/sonnet-review` is a project skill that reviews the current git diff — for
correctness bugs, security, and the project's DRY/SOLID/layering rules — on the
**Sonnet** model in an isolated context. It's read-only; run it before committing
or opening a PR:

```
/sonnet-review            # this branch's diff vs main
/sonnet-review staged     # only staged changes
/sonnet-review backend/src
```
