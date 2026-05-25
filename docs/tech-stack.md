# openruki — Tech Stack & Next Steps

This is the planned stack for building openruki. It covers the parts we control (the add-on's own frontend and backend). The rest — how features get generated into the *host* project — depends on whatever that host project is built with.

## Frontend (openruki's own UI)

The UI the self-hoster logs into and uses to describe features.

- **Vite** — build tool / dev server
- **React** — UI framework
- **TypeScript** — language
- **TanStack Query** — server state / data fetching

## Backend (openruki's own API)

- **FastAPI (Python)** — API server
- **Python** — language for backend + API logic

## The agent

The agent that actually builds the requested feature into the host deployment.

- **Undecided for now.** How it works and how it integrates with the host project's code is still open.

## What depends on the host project

openruki sits *inside* a self-hosted open-source project. So a lot is determined by that host:

- The language/framework of the generated feature code (matches the host).
- How openruki reads and writes the host's pages/code.
- How auth lines up with the host (see vision.md open questions).

→ See [vision.md](./vision.md) for the product flow and open questions.

## Stack at a glance

| Layer | Choice |
|---|---|
| Frontend build | Vite |
| Frontend framework | React + TypeScript |
| Frontend data | TanStack Query |
| Backend API | FastAPI (Python) |
| Agent | TBD |
| Generated feature code | depends on host project |
