# openruki — Vision

## One-liner

**openruki is an embeddable plugin that brings low-code into existing open-source products.**
Maintainers drop it into their project; their users describe a feature they want, and openruki's AI generates the code to build it — either for the whole project or just for a single self-hosted instance.

## The bet (thesis)

Low-code today is good at building *new* apps from scratch. The real gap is **adding low-code _into_ existing, mature products.**

Open-source products are powerful but rigid. Users constantly want features the maintainers can't ship fast enough — and self-hosters want tweaks that only make sense for their own deployment. openruki turns "I wish this app could do X" into a working feature, without forking the codebase or waiting on a roadmap.

## How it works

1. **Maintainer installs openruki** as a plugin/extension on top of their open-source project.
2. **A user requests a feature** in plain language. *Example: in an open-source WhatsApp, a user asks for "private status — visible to selected people only."*
3. **openruki asks who it's for:**
   - **Project-wide** → the maintainer/admin approves, and the feature is built for *everyone* on the project.
   - **Instance-only** → a self-hoster builds it for *their own deployment* only.
4. **AI generates the code** — primarily backend logic plus the wiring into the existing product — and integrates it.

Because openruki lives inside the host product, generated features reuse the product's existing patterns and conventions rather than living as a bolted-on separate app.

## Who it's for

- **OSS maintainers** — give their community a way to extend the product, and a path to approve/ship the good ideas to everyone.
- **Self-hosters** — customize their own instance freely, without forking or maintaining patches.

(End users benefit indirectly: the features they want actually get built.)

## Why "open" + the name

openruki is itself open-source and designed to sit on top of *other* open-source projects — an extension layer that any project can adopt to give its users feature-building superpowers.

## Open questions / TODO

- [ ] Monetization model (premium features? hosted build service? per-instance licensing?)
- [ ] First target host project to prototype against (e.g. an open-source chat app)
- [ ] How generated features are reviewed, tested, and merged safely
- [ ] Boundary between "config toggle" features and "AI-generated code" features
- [ ] Sandboxing / security model for AI-generated code in production
