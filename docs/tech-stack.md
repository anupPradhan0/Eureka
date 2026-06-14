# Eureka — Tech Stack & Next Steps

This is the planned stack for building Eureka. It covers the parts we control (the add-on's own frontend and backend). The rest — how features get generated into the *host* project — depends on whatever that host project is built with.

## Frontend (Eureka's own UI)

The UI the self-hoster logs into and uses to describe features.

- **Vite** — build tool / dev server
- **React** — UI framework
- **TypeScript** — language
- **TanStack Query** — server state / data fetching

## Backend (Eureka's own API)

- **FastAPI (Python)** — API server
- **Python** — language for backend + API logic
- **MongoDB** — data store (users, AI config, imported repos)

## AI access (bring your own key)

Eureka ships **no AI access of its own** — being open-source, each self-hoster
supplies their own key. The user configures a provider, model, and API key, which
is validated live and stored encrypted at rest.

- **Providers:** Anthropic, OpenAI, OpenRouter, Google Gemini
- This configures *which model Eureka uses*; the agent that consumes it is below.

## The agent

The agent that actually builds the requested feature into the host deployment.

- **Undecided for now.** How it works and how it integrates with the host project's code is still open.

## What depends on the host project

Eureka sits *inside* a self-hosted open-source project. So a lot is determined by that host:

- The language/framework of the generated feature code (matches the host).
- How Eureka reads and writes the host's pages/code.
- How auth lines up with the host (see vision.md open questions).

→ See [vision.md](./vision.md) for the product flow and open questions.

## Stack at a glance

| Layer | Choice |
|---|---|
| Frontend build | Vite |
| Frontend framework | React + TypeScript |
| Frontend data | TanStack Query |
| Backend API | FastAPI (Python) |
| Data store | MongoDB |
| AI access | BYO key — Anthropic / OpenAI / OpenRouter / Gemini |
| Agent | TBD |
| Generated feature code | depends on host project |
