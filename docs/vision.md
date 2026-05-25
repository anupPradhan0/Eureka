# openruki — Vision

## One-liner

**openruki is an installable add-on that brings low-code into self-hosted open-source products.**
Someone deploys an open-source project, installs openruki inside it, and then — through a simple frontend — describes the feature they want in plain language. openruki's agent builds it into their own deployment.

## Focus: self-hosted, for now

The broad "ship a feature to the whole project for everyone" idea is a hassle to get right today, so it's **deferred.**

**Phase 1 is the self-hosted open-source project.** The target user is someone who took an open-source project, deployed their own copy, and wants to add features specific to *their* instance — but **doesn't know how to code it.** openruki is how they get those features without touching the codebase.

## The bet (thesis)

Low-code today is good at building *new* apps from scratch. The real gap is **adding low-code _into_ existing, mature products.**

Open-source products are powerful but rigid. Self-hosters constantly want tweaks that only make sense for their own deployment, but they don't have the skills (or time) to implement them. openruki turns "I wish my instance could do X" into a working feature — no fork, no patches to maintain, no waiting on a roadmap.

## How it works (the blueprint)

1. **The host project is deployed.** A user self-hosts an open-source project (the "foundation project").
2. **They install openruki inside it** as an add-on.
3. **openruki gives them a frontend UI.** They log in with email + password.
4. **They point at what they want to change** — which page / which part of the product they want to build something on, and import/select it.
5. **They give the command** — in plain language, they describe the feature they want added to their self-hosted instance.
6. **The openruki agent builds it** into their deployment.

Because openruki lives inside the host product, generated features reuse the product's existing patterns and conventions rather than living as a bolted-on separate app.

## Who it's for

- **Self-hosters of open-source projects** (Phase 1) — people running their own copy who want instance-specific features but can't build them by hand.
- **OSS maintainers / project-wide rollout** — *deferred to a later phase.*

## Why "open" + the name

openruki is itself open-source and designed to sit on top of *other* open-source projects — an extension layer that any project can adopt to give its users feature-building superpowers.

## Open questions / TODO

- [ ] How the add-on installs into an arbitrary host project (package? sidecar service? code injection?)
- [ ] How openruki gets enough access to the host's pages/code to build into them safely
- [ ] First target host project to prototype against (e.g. an open-source chat app)
- [ ] Auth: is the email+password login openruki's own, or tied to the host project's accounts?
- [ ] Sandboxing / security model for AI-generated code in production
- [ ] Monetization model (premium features? hosted build service? per-instance licensing?)
- [ ] When/how to revisit project-wide rollout (Phase 2)
