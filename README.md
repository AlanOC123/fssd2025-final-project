# Apex

A full-stack personal training platform that connects trainers and clients. Trainers build structured programs with phases and workouts, clients complete sessions, and the analytics engine tracks 1RM progression and session load over time.

Built as a capstone project for a Full Stack Development diploma.

---

## Tech Stack

**Backend** — Django 5.2 · Django REST Framework · dj-rest-auth · allauth · SimpleJWT (httpOnly cookies) · PostgreSQL 18 · Cloudinary · Anymail (Brevo)

**Frontend** — React 19 · Vite · TanStack Router · TanStack Query · TanStack Form · Zustand · Zod · Tailwind v4 · shadcn/ui · Recharts

**Infrastructure** — Docker Compose (3 services) · Render (production)

---

## Local Development

### Prerequisites

- Docker and Docker Compose
- Node 20+ and pnpm

### Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd apex

# 2. Create backend environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your local values (see Environment Variables below)

# 3. Start all services
docker-compose up

# 4. In a separate terminal — seed the database
./scripts/db/seed

# 5. Seed the demo environment (trainer + client + programs + workout history)
./scripts/backend/manage seed_demo

# 6. Backfill analytics snapshots for the demo data
./scripts/backend/manage backfill_snapshots
```

The app will be available at:
- **Frontend** — http://localhost:5173
- **Django API** — http://localhost:8000
- **Django Admin** — http://localhost:8000/admin

### Demo Accounts

After running `seed_demo`:

| Role    | Email             | Password   |
|---------|-------------------|------------|
| Trainer | trainer@apex.com  | password123 |
| Client  | demo@apex.com     | password123 |

---

## Project Structure

```
apex/
├── backend/                  # Django project
│   ├── apps/
│   │   ├── analytics/        # 1RM + session load snapshots
│   │   ├── biology/          # Muscle/joint reference data
│   │   ├── energy/           # Energy system models
│   │   ├── exercises/        # Exercise library
│   │   ├── notifications/    # Notification models
│   │   ├── programs/         # Programs, phases, phase options
│   │   ├── users/            # CustomUser, TrainerProfile, ClientProfile, memberships
│   │   └── workouts/         # Workouts, exercises, sets + completion records
│   └── core/                 # Django settings, URLs, WSGI
├── frontend/                 # React application
│   └── src/
│       ├── app/              # Router, providers, constants
│       ├── features/         # Feature-sliced modules
│       │   ├── analytics/    # Load history charts
│       │   ├── auth/         # Login, register, forgot/reset password
│       │   ├── memberships/  # Trainer-client membership flow
│       │   ├── profile/      # Client profile
│       │   ├── programs/     # Program + phase management
│       │   ├── trainers/     # Trainer profile + client matching
│       │   └── workouts/     # Workout builder + client session
│       ├── routes/           # TanStack Router file-based routes
│       └── shared/           # UI components, hooks, utils
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
- Upload profile avatar and manage training profile

### Auth
- Email-based registration with role selection (Trainer / Client)
- httpOnly JWT cookies (access + refresh) with automatic token refresh
- Forgot password / reset password flow

---

## Environment Variables

### Backend (`backend/.env`)

```env
# Core
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgres://admin:password123@db:5432/apex_training

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
CORS_TRUSTED_ORIGINS=http://localhost:5173

# Email (dev uses console backend — emails print to terminal)
DEFAULT_FROM_EMAIL=dev@localhost

# Password reset frontend URL
PASSWORD_RESET_LINK=http://localhost:5173/reset-password

# Production only (not required for local dev)
# BREVO_API_KEY=
# CLOUDINARY_API_KEY=
# CLOUDINARY_API_SECRET_KEY=
# CLOUD_NAME=
# NINJA_API_KEY=
```

---

## Running Tests

```bash
# Run all backend tests
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

The `render.yaml` at the root of the repo configures two services and a managed Postgres database:

| Service | Type | Description |
|---------|------|-------------|
| `apex-api` | Web service (Python) | Django + Gunicorn |
| `apex-app` | Web service (Node) | React static build served via `serve` |
| `apex-db` | PostgreSQL | Managed database |

### Steps

1. Push the repo to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your GitHub repo — Render will detect `render.yaml` automatically
4. Set the `sync: false` environment variables in the Render dashboard:
   - `BREVO_API_KEY`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET_KEY`
   - `CLOUD_NAME`
5. Update `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `PASSWORD_RESET_LINK` with your actual Render service URLs once they're generated
6. Deploy

### Post-deploy

```bash
# Seed reference data (run via Render shell on apex-api)
python manage.py seed_db

# Optionally seed demo data
python manage.py seed_demo
python manage.py backfill_snapshots
```

---

## Architecture Notes

**Auth flow** — Registration and login both set httpOnly JWT cookies via dj-rest-auth. The Axios client has a response interceptor that queues 401 responses and attempts a token refresh before retrying. The `_auth` route guard reads from the Zustand store directly (not router context) to avoid stale context flashes after login/registration.

**Analytics** — `ExerciseSessionSnapshot` is computed and stored when a client calls `finish_workout`. Each snapshot stores the rolling 1RM (Epley formula), session load (Σ reps × weight), target load, and weight band derived from NSCA progression tables. The `backfill_snapshots` management command retroactively computes snapshots for seeded demo data.

**Status codes** — The backend uses `LabelLookupSerializer` for some status fields which returns only `{ id, label }` without a `code` field. The frontend normalises this with label-to-code maps so filtering works regardless of serializer version.
