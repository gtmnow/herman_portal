# Herman Portal

Temporary standalone login portal for HermanPrompt.

This repo provides:

- email/password login
- password reset flow scaffolding
- launch token minting for HermanPrompt
- hooks for Herman Admin-managed invitation acceptance and tenant branding

The portal is designed to use the same Postgres database as HermanPrompt and Herman Admin.

## Repo Layout

```text
backend/    FastAPI backend
frontend/   Vite + React frontend
docs/       build spec and deployment notes
```

## Current Status

This repo is scaffolded and ready for implementation.

- build spec is in `docs/BUILD_SPEC.md`
- deployment guide is in `docs/DEPLOYMENT.md`
- admin-tool integration contract is in `docs/ADMIN_TOOL_DATA_CONTRACT.md`
- backend app structure is in place
- frontend app structure is in place
- auth, password reset, and admin hook boundaries are stubbed
- local bootstrap scripts exist for initializing auth tables and creating users

## Admin Tool Integration

Herman Portal must consume tenant-owned portal configuration and invitation data written by Herman Admin.

The current contract is documented in:

- `docs/ADMIN_TOOL_DATA_CONTRACT.md`

In practice, that means Herman Portal should read:

- `tenant_portal_configs` for portal URL, logo, and welcome message
- `user_invitations` for invitation acceptance state and 7-day TTL
- `auth_users` as the source of truth for authenticated users

## Next Steps

1. Create the backend virtual environment and install dependencies.
2. Install frontend dependencies.
3. Set `DATABASE_URL` or `DATABASE_PUBLIC_URL` in `backend/.env`.
4. Run migrations with `python -m app.scripts.init_db`.
5. Align the auth schema and routes with the admin contract in `docs/ADMIN_TOOL_DATA_CONTRACT.md`.
6. Implement `/invite` so users can accept invitations and set their initial passwords.
7. Continue wiring the remaining auth flows and UI polish.

## Database Setup

Place your shared Postgres connection string in:

- `/Users/michaelanderson/projects/herman_portal/backend/.env`

Use either:

```env
DATABASE_URL=postgresql+psycopg://...
```

or:

```env
DATABASE_PUBLIC_URL=postgresql+psycopg://...
```

If your host gives you `postgres://...` or `postgresql://...`, that is okay too.
The backend now normalizes those to the installed `psycopg` driver automatically.

Then run:

```bash
cd /Users/michaelanderson/projects/herman_portal/backend
python -m app.scripts.init_db
```
