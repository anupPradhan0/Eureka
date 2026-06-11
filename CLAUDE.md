# CLAUDE.md

## About the Project

**openruki** is a low-code add-on installed *inside* self-hosted open-source apps. The user deploys their own copy of an open-source product (the "foundation project"), drops openruki inside it, logs in, points at a page, and describes a feature in plain language — openruki's AI agent builds that feature directly into their instance. No fork, no patches, no coding required.

The gap it fills: low-code today builds *new* apps, but openruki adds low-code *into* existing mature products, so self-hosters can get custom tweaks without the skills or time to code them.

- **Frontend:** Vite + React + TypeScript + TanStack Query
- **Backend:** FastAPI (Python)
- **Agent:** TBD
- **Status:** Early scaffolding; Phase 1 focuses on self-hosted deployments.

## Core Principles

Write all code following these principles:

- **DRY (Don't Repeat Yourself)** — No duplicated logic. Extract shared code into reusable functions/modules.
- **SOLID** — Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion.
- **Maintainability** — Code is easy to change and extend.
- **Readability** — Clear naming, consistent style, self-explanatory code.
- **Efficiency** — Performant, no wasteful operations.
- **Testability** — Code is structured so it can be unit-tested in isolation.
- **Security** — Validate input, handle errors safely, never expose secrets.

## Repository Structure

Use a **monorepo** (monolithic repository). Keep all code in one repository with a consistent structure — do not split into mixed or inconsistent layouts.

## Standard Layout

```
src/
├── config/                  # Database connections & system configurations
├── routes/                  # Route definitions; maps requests to controllers
│   └── user_routes.js
├── controllers/             # Handles HTTP request/response loops
│   └── user_controller.js
├── services/                # Business logic layer; calls the repositories
│   └── user_service.js
├── repositories/            # Data access encapsulation
│   ├── interfaces/          # Abstraction definitions (if language uses them)
│   │   └── iuser_repository.js
│   ├── base_repository.js   # Optional generic CRUD repository
│   └── user_repository.js   # Concrete database implementation
├── models/                  # Database schemas or ORM entities (Mongoose, Sequelize)
│   └── user_model.js
└── app.js                   # Application entry point
```

**Request flow:**

```
Request
   ↓
Routes
   ↓
Controller
   ↓
Service
   ↓
Repository
   ↓
MongoDB Model
```

**Layering rule:** routes → controllers → services → repositories → models. Each layer only talks to the layer directly below it.

## Package Manager

Use **pnpm** for all package management and scripts. Do not use npm or yarn.

## Communication Style

- Answer only what is asked. No extra jargon, no filler, no unrequested information.
- Give direct answers.
- If a question can be answered with yes or no, answer just yes or no.
