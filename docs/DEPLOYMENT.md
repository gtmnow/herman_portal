# Deployment Guide

## Overview

Herman Portal deploys as two Railway services:

- frontend service
- backend service

The portal is the production login entrypoint for HermanPrompt.

## Service Layout

### Frontend service

- Root directory: `frontend`
- Purpose: serve the login, forgot-password, reset-password, and change-password UI

### Backend service

- Root directory: `backend`
- Purpose: authenticate users, issue signed launch tokens, manage password reset/change flows

## Railway Backend Configuration

### Build and start

- Build command:

```bash
pip install -r requirements.txt
```

- Start command:

```bash
python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Required environment variables

- `DATABASE_PUBLIC_URL=<shared Postgres url used by HermanPrompt>`
- `HERMANPROMPT_UI_URL=https://herman-prompt-demo-production-5b99.up.railway.app`
- `PORTAL_UI_URL=https://hermanportal-production.up.railway.app`
- `HERMANPROMPT_LAUNCH_SECRET=<must exactly match HermanPrompt backend AUTH_LAUNCH_SECRET>`
- `LAUNCH_TOKEN_TTL_SECONDS=3600`
- `PASSWORD_RESET_TOKEN_TTL_SECONDS=1800`
- `DEV_SHOW_RESET_LINKS=false`
- `CORS_ALLOWED_ORIGINS=https://hermanportal-production.up.railway.app`
- `APP_ENV=production`
- `HOST=0.0.0.0`

Notes:

- the backend accepts either `DATABASE_URL` or `DATABASE_PUBLIC_URL`
- `postgres://...` and `postgresql://...` are normalized to the installed `psycopg` driver automatically
- because the database is shared with other services, Herman Portal uses its own Alembic version table: `alembic_version_herman_portal`

## Railway Frontend Configuration

### Build and start

- Build command:

```bash
npm install && npm run build
```

- Start command:

```bash
npx serve -s dist -l $PORT
```

### Required environment variables

- `VITE_API_BASE_URL=https://hermanportal-production-8c42.up.railway.app`

Important:

- `VITE_*` variables are read at build time
- changing `VITE_API_BASE_URL` requires a new frontend deploy

## Production Flow

1. user opens Herman Portal frontend
2. user logs in with email and password
3. Herman Portal backend validates credentials against the shared Postgres database
4. Herman Portal backend signs launch token
5. Herman Portal frontend redirects user into HermanPrompt frontend
6. HermanPrompt backend validates the launch token and creates the app session

## Local And Production Data Setup

### Run migrations

```bash
cd backend
python -m app.scripts.init_db
```

### Create a user

```bash
cd backend
python -m app.scripts.create_user \
  --email you@example.com \
  --password password123 \
  --user-id-hash user_1 \
  --display-name "Test User 1"
```

## Common Deployment Issues

### `Invalid token signature`

Cause:

- `HERMANPROMPT_LAUNCH_SECRET` does not match HermanPrompt backend `AUTH_LAUNCH_SECRET`

Fix:

- make the two values identical
- redeploy Herman Portal backend
- redeploy HermanPrompt backend
- log in again to generate a fresh launch token

### Backend fails during migration

Common causes:

- shared database already has another service’s `alembic_version` table
- missing `DATABASE_PUBLIC_URL` or `DATABASE_URL`
- unsupported connection string format

Fix:

- use the portal’s Alembic setup, which writes to `alembic_version_herman_portal`
- set `DATABASE_PUBLIC_URL` or `DATABASE_URL` on the backend service
- confirm the URL points to the shared Postgres database

### Frontend redirects but login API fails

Common causes:

- missing or incorrect `VITE_API_BASE_URL`
- backend CORS mismatch
- portal backend is down

## Production Verification Checklist

1. portal login page loads
2. valid login redirects into HermanPrompt
3. HermanPrompt loads without auth error
4. direct anonymous use of HermanPrompt is not the intended production path
5. forgot-password flow returns accepted response
6. change-password flow succeeds
7. new password works and old password fails
