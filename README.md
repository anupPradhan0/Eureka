# openruki

**Low-code, built _into_ your self-hosted open-source apps.**

openruki is an installable add-on for self-hosted open-source projects. You deploy
your own copy of an open-source product, drop openruki inside it, log in, point at a
page, and describe the feature you want in plain language — openruki's agent builds it
into your instance. No fork, no patches to maintain, no coding required.

## Why

Low-code today is great at building *new* apps. The gap is adding low-code *into*
existing, mature products. Self-hosters constantly want tweaks specific to their own
deployment but don't have the skills or time to implement them. openruki turns
"I wish my instance could do X" into a working feature.

## How it works

1. Self-host an open-source project (the "foundation project").
2. Install openruki inside it as an add-on.
3. Log in to openruki's UI (email + password).
4. Point at the page / part you want to change.
5. Describe the feature you want.
6. The openruki agent builds it into your deployment.

## Tech stack

- **Frontend:** Vite + React + TypeScript + TanStack Query
- **Backend:** FastAPI (Python)
- **Agent:** TBD

## Status

Early / scaffolding. Phase 1 focuses on **self-hosted** deployments; project-wide
rollout for maintainers is deferred to a later phase.

## Docs

- [Vision](./docs/vision.md) — product vision, user flow, open questions
- [Tech Stack & Next Steps](./docs/tech-stack.md) — stack and what's still undecided

## Repository layout

```
backend/    FastAPI app (routes → services → repositories → models)
frontend/   Vite + React + TypeScript app
docs/        vision and tech-stack docs
```
