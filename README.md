# Apex

A full-stack personal training platform that connects trainers and clients. Trainers build structured programs with phases and workouts, clients complete sessions, and the analytics engine tracks 1RM progression and session load over time.

Built as a capstone project for a Full Stack Development diploma.

**Live:** https://apex-app-ar64.onrender.com

---

## Tech Stack

**Backend** — Django 5.2 · Django REST Framework · dj-rest-auth · allauth · SimpleJWT (httpOnly cookies) · PostgreSQL 18 · Cloudinary · Anymail (Brevo)

**Frontend** — React 19 · Vite · TanStack Router · TanStack Query · TanStack Form · Zustand · Zod · Tailwind v4 · shadcn/ui · Recharts

**Infrastructure** — Docker Compose (3 services) · Render (production)

---

## Local Development

### Prerequisites

- Docker and Docker Compose
- Node 20+ and pnpm (`npm install -g pnpm`)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/AlanOC123/fssd2025-final-project
cd fssd2025-final-project

# 2. Create backend environment file
cp backend/.env.example backend/.env
# Edit backend/.env — minimum required values listed under Environment Variables

# 3. Start all services
docker-compose up

# 4. In a separate terminal — run migrations and seed reference data
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_db

# 5. Seed demo accounts, programs, and workout history
docker-compose exec web python manage.py seed_demo

# 6. Backfill analytics snapshots for the demo data
docker-compose exec web python manage.py backfill_snapshots
```

The app will be available at:
- **Frontend** — http://localhost:5173
- **Django API** — http://localhost:8000
- **Django Admin** — http://localhost:8000/admin

### Demo Accounts

| Role    | Email            | Password    |
|---------|------------------|-------------|
| Trainer | trainer@apex.com | password123 |
| Client  | demo@apex.com    | password123 |

(See Full List in seed_users_demo_data.json)

---

## Project Structure

```
apex/
├── backend/                  # Django project
│   ├── apps/
│   │   ├── analytics/        # 1RM + session load snapshots
│   │   ├── biology/          # Muscle/joint reference data
│   │   ├── energy/           # Energy system models (Out of Scope)
│   │   ├── exercises/        # Exercise library + external API enrichment
│   │   ├── notifications/    # Notification models (Out of Scope)
│   │   ├── programs/         # Programs, phases, phase options
│   │   ├── users/            # CustomUser, TrainerProfile, ClientProfile, memberships
│   │   └── workouts/         # Workouts, exercises, sets + completion records
│   └── core/                 # Django settings, URLs, WSGI
├── frontend/                 # React application
│   └── src/
│       ├── app/              # Router, providers, constants
│       ├── features/         # Feature-sliced modules
│       │   ├── analytics/    # Load history charts (Recharts)
│       │   ├── auth/         # Login, register, forgot/reset password
│       │   ├── clients/      # Trainer's client management views
│       │   ├── dashboard/    # Trainer + client dashboards
│       │   ├── memberships/  # Trainer-client membership flow
│       │   ├── profile/      # Trainer + client profile pages
│       │   ├── programs/     # Program + phase management
│       │   ├── trainers/     # Trainer matching + find trainer
│       │   └── workouts/     # Workout builder + client session
│       ├── routes/           # TanStack Router file-based routes
│       └── shared/           # UI components, hooks, utils, Axios client
├── scripts/                  # Dev utility scripts
├── docker-compose.yml
└── render.yaml               # Render deployment config
```

---

## Key Features

### Trainer
- Create training programs with structured phases (Accumulation, Intensification, etc.)
- Build workouts with exercises, sets, reps, and weight targets
- Manage client memberships — accept/reject requests
- View per-exercise analytics: estimated 1RM and session load over time (7D / 1M / Phase / 3M / 1Y)
- Upload company logo and set specialisms (goals + experience levels) for client matching

### Client
- Browse and request trainers matched to their goal and experience level
- Complete workouts session by session with set-level tracking
- View upcoming, missed, and completed workouts
- Upload profile avatar and manage training profile (goal + experience level)

### Auth
- Email-based registration with role selection (Trainer / Client)
- httpOnly JWT cookies (access + refresh) with automatic token refresh via Axios interceptor
- Forgot password / reset password flow via Brevo email (production) or console (development)

---

## Environment Variables

### Backend (`backend/.env`)

```env
# Core
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# Database — matches docker-compose.yml defaults
DATABASE_URL=postgres://admin:password123@db:5432/apex_training

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
CORS_TRUSTED_ORIGINS=http://localhost:5173

# Email — dev uses console backend, emails print to Django logs
DEFAULT_FROM_EMAIL=dev@localhost

# Password reset — URL embedded in reset emails
PASSWORD_RESET_LINK=http://localhost:5173/reset-password

# Exercise enrichment API (optional in dev — file is cached after first run)
NINJA_API_KEY=

# Production only — not required for local dev
# BREVO_API_KEY=
# CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
# CLOUDINARY_API_KEY=
# CLOUDINARY_API_SECRET_KEY=
# CLOUD_NAME=

# Set to true to test Cloudinary uploads locally without full production mode
# Requires CLOUDINARY_URL to also be set
# USE_CLOUDINARY=true
```

---

## Running Tests

```bash
# Run the full backend test suite
./scripts/backend/test-all

# Run tests for a specific app
./scripts/backend/test-app users
./scripts/backend/test-app programs
./scripts/backend/test-app workouts
./scripts/backend/test-app analytics
```

The test suite has 259 passing tests across all apps.

---

## Deployment (Render)

The `render.yaml` at the root configures two services and a managed Postgres database.

| Service | Type | Description |
|---------|------|-------------|
| `apex-api` | Web (Python) | Django + Gunicorn |
| `apex-app` | Static (Node) | React — built with Vite, served via Render CDN |
| `apex-db` | PostgreSQL | Managed Postgres |

The frontend routes `/api/*` requests to the backend via a Render rewrite rule, mirroring the Vite dev proxy.

### Steps

1. Push the repo to GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect the GitHub repo — Render detects `render.yaml` automatically
4. During the Blueprint creation flow, fill in the `sync: false` env vars when prompted:

| Key | Value |
|-----|-------|
| `ALLOWED_HOSTS` | `your-apex-api-xxxx.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://your-apex-app-xxxx.onrender.com` |
| `CORS_TRUSTED_ORIGINS` | `https://your-apex-app-xxxx.onrender.com` |
| `PASSWORD_RESET_LINK` | `https://your-apex-app-xxxx.onrender.com/reset-password` |
| `DEFAULT_FROM_EMAIL` | Your verified Brevo sender address |
| `BREVO_API_KEY` | Brevo dashboard → SMTP & API → API Keys |
| `CLOUDINARY_URL` | `cloudinary://api_key:api_secret@cloud_name` |
| `CLOUDINARY_API_KEY` | Cloudinary dashboard |
| `CLOUDINARY_API_SECRET_KEY` | Cloudinary dashboard |
| `CLOUD_NAME` | Cloudinary dashboard |
| `NINJA_API_KEY` | API Ninjas dashboard |

5. After the services spin up and URLs are assigned, update the rewrite rule in `apex-app` → **Redirects/Rewrites**:
   - **Source:** `/api/*`
   - **Destination:** `https://your-apex-api-xxxx.onrender.com/api/*`

6. **First deploy only** — temporarily add seed commands to the `apex-api` build command via the Render dashboard:
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py seed_db && python manage.py seed_demo && python manage.py backfill_snapshots
   ```
   After a successful deploy, revert to:
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py seed_db
   ```
   Demo data persists in the database between deploys.

### Known Deployment Issues & Solutions

**`django-cloudinary-storage` compatibility with Django 5**
This package (v0.3.0, last updated 2020) references `STATICFILES_STORAGE` which was removed in Django 5. A compatibility alias is set in `settings.py`. Do not define a `CLOUDINARY_STORAGE` dict in settings — the package reads `CLOUDINARY_URL` directly from the environment, and settings values take precedence over env vars and will override it.

**Static files / collectstatic**
`collectstatic` is intentionally omitted from the build command. The backend is API-only; Whitenoise is not used. Django admin CSS is served directly by Django's built-in static file handling without any post-processing.

**Render rewrite rule syntax**
Use `*` in the destination, not `:splat` (which is Netlify syntax):
- ✓ `https://apex-api-xxxx.onrender.com/api/*`
- ✗ `https://apex-api-xxxx.onrender.com/api/:splat`

**Service URLs change on rebuild**
Deleting and recreating the Blueprint generates new subdomain slugs. Update `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CORS_TRUSTED_ORIGINS`, `PASSWORD_RESET_LINK`, and the rewrite destination each time.

**Free tier cold starts**
The backend spins down after 15 minutes of inactivity and takes ~30 seconds to cold start on the first request. Load the app once before a demo to warm it up.

**FormData / file uploads**
The Axios client has a request interceptor that deletes the `Content-Type` header for `FormData` requests. This allows Axios to set the correct `multipart/form-data; boundary=...` header automatically. Do not manually set `Content-Type` on file upload requests — it will strip the boundary and Django won't be able to parse the file.

---

## Architecture Notes

**Auth flow** — Registration calls `POST /auth/registration/` then immediately `POST /auth/login/` with the same credentials to set JWT cookies reliably. The `_auth` route guard reads `isAuthenticated` from the Zustand store via `getState()` rather than router context, avoiding stale context flashes during post-login navigation.

**Analytics** — `ExerciseSessionSnapshot` is computed and stored when a client calls `finish_workout`. Each snapshot stores the rolling 1RM (Epley formula), session load (Σ reps × weight), target load, and weight band derived from NSCA progression tables. The `backfill_snapshots` management command retroactively computes snapshots for seeded demo data that bypasses `finish_workout`.

**Password reset** — Django's default `PasswordResetConfirmSerializer` expects integer PKs. `ApexPasswordResetConfirmSerializer` handles UUID PKs by decoding the base64 `uid` to a UUID string directly. `ApexPasswordResetSerializer` bypasses allauth's `reverse('password_reset_confirm')` (which doesn't exist in API-only mode) and builds the reset URL from `PASSWORD_RESET_LINK` directly.

**Status codes** — Some serializers return `{ id, label }` without a `code` field. Affected frontend components normalise this with label-to-code maps so filtering works regardless of which serializer version is active.

**Exercise cache** — `apps/exercises/management/commands/enrichment_data.json` is gitignored. The exercise seeding command calls the API Ninjas external API on first run and caches the response locally. In production the file does not exist so the external API is always called during `seed_db`.
