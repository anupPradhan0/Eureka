# Eureka — frontend

Vite + React + TypeScript + TanStack Query. This is the UI a self-hoster logs
into to configure Eureka and import the repository they want to build into.

## Onboarding flow

`src/App.tsx` is a gated step resolver driven by TanStack Query state — each step
unlocks the next:

1. **Not authenticated** → `AuthPage` (login / register)
2. **No AI config** → `ConfigPage` (provider, model, API key — validated live)
3. **No repository** → `RepoImportPage` (GitHub URL + optional token)
4. **Ready** → `RepoSummaryPage` (stats, file tree, docs, README)

## Structure

```
src/
├── api/          # one module per backend area; all HTTP goes through client.ts
├── hooks/        # TanStack Query hooks (components never call api/ directly)
├── pages/        # one screen per onboarding step
├── components/   # reusable UI (AppShell, StatBadge, FileTree, DocList, MarkdownView)
├── types/        # DTO types mirroring the backend
├── lib/          # token storage
├── providers/    # QueryProvider
└── config/       # env.ts — the only reader of import.meta.env
```

The backend base URL comes from `VITE_API_URL` (copy `.env.example` to `.env`).

## Scripts

```bash
pnpm install
pnpm dev       # dev server + HMR
pnpm build     # type-check (tsc) + production build
pnpm lint
```

Use **pnpm** (not npm/yarn). In the Docker dev stack (`docker compose up` from the
repo root) this runs automatically with hot reload.
