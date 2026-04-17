# Herman Portal

Temporary standalone login portal for HermanPrompt.

This repo provides:

- email/password login
- password reset flow scaffolding
- launch token minting for HermanPrompt
- hooks for a future Herman admin portal

The portal is designed to use the same Postgres database as HermanPrompt.

## Repo Layout

```text
backend/    FastAPI backend
frontend/   Vite + React frontend
docs/       build spec and implementation notes
```

## Current Status

This repo is scaffolded and ready for implementation.

- build spec is in `docs/BUILD_SPEC.md`
- backend app structure is in place
- frontend app structure is in place
- auth, password reset, and admin hook boundaries are stubbed

## Next Steps

1. Create the backend virtual environment and install dependencies.
2. Install frontend dependencies.
3. Implement the shared database models and migrations.
4. Wire login, password reset, and HermanPrompt redirect flows.
