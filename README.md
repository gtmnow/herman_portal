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
docs/       build spec and deployment notes
```

## Current Status

This repo is scaffolded and ready for implementation.

- build spec is in `docs/BUILD_SPEC.md`
- deployment guide is in `docs/DEPLOYMENT.md`
- backend app structure is in place
- frontend app structure is in place
- auth, password reset, and admin hook boundaries are stubbed
- local bootstrap scripts exist for initializing auth tables and creating users

## Next Steps

1. Create the backend virtual environment and install dependencies.
2. Install frontend dependencies.
3. Set `DATABASE_URL` or `DATABASE_PUBLIC_URL` in `backend/.env`.
4. Run migrations with `python -m app.scripts.init_db`.
5. Create a test user with `python -m app.scripts.create_user --email ... --password ... --user-id-hash user_1`.
6. Continue wiring the remaining auth flows and UI polish.

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
