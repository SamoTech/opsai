# Deploying OpsAI on Vercel

OpsAI uses a **split deployment** strategy on Vercel:

| Service | Deployment | Notes |
|---------|-----------|-------|
| Frontend (Next.js) | Vercel Project | Auto-deploy on push |
| Backend (FastAPI) | Vercel Serverless | Python ASGI via `@vercel/python` |
| PostgreSQL | Vercel Postgres / Neon | Managed DB |
| Redis | Upstash Redis | Serverless-compatible Redis |
| Celery Workers | **Not on Vercel** | Use Railway / Render / VPS |

> ⚠️ **Note:** Celery background workers require a persistent process and cannot run on Vercel's serverless platform. Deploy workers separately on Railway, Render, or a VPS.

---

## Step 1 — Set Up External Services

### PostgreSQL (Neon — Free Tier)
1. Go to [neon.tech](https://neon.tech) → Create project
2. Copy the connection string: `postgresql://user:pass@ep-xxx.neon.tech/opsai`

### Redis (Upstash — Free Tier)
1. Go to [upstash.com](https://upstash.com) → Create Redis database
2. Copy the `REDIS_URL`: `rediss://default:xxx@xxx.upstash.io:6379`

---

## Step 2 — Deploy Backend to Vercel

```bash
cd backend
npx vercel
```

Or connect via Vercel dashboard:
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `SamoTech/opsai` repo
3. Set **Root Directory** to `backend`
4. Framework: **Other**
5. Add environment variables (see below)

### Backend Environment Variables

| Variable | Value |
|----------|-------|
| `APP_SECRET_KEY` | `openssl rand -hex 32` |
| `DATABASE_URL` | Your Neon PostgreSQL URL |
| `REDIS_URL` | Your Upstash Redis URL |
| `GROQ_API_KEY` | From [console.groq.com](https://console.groq.com) |
| `GITHUB_WEBHOOK_SECRET` | Any random string |
| `SLACK_BOT_TOKEN` | Optional |

---

## Step 3 — Deploy Frontend to Vercel

```bash
cd frontend
npx vercel
```

Or via dashboard:
1. New project → Import same repo
2. Set **Root Directory** to `frontend`
3. Framework: **Next.js** (auto-detected)
4. Add environment variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Your backend Vercel URL (e.g. `https://opsai-api.vercel.app`) |

---

## Step 4 — Update CORS

After getting your frontend Vercel URL, update the backend env variable:

```env
ALLOWED_ORIGINS=["https://opsai-frontend.vercel.app"]
```

Or set it in Vercel dashboard under backend project → Settings → Environment Variables.

---

## Step 5 — Run Database Migrations

Since Alembic can't run on Vercel, run migrations locally against your Neon DB:

```bash
cd backend
export DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/opsai"
alembic upgrade head
```

---

## Step 6 — Deploy Celery Worker (Railway)

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select `SamoTech/opsai` → Root directory: `backend`
3. Set start command:
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```
4. Add same environment variables as backend

---

## Architecture on Vercel

```
┌──────────────────────────────────┐
│           Vercel Edge                 │
├───────────────┼──────────────────┤
│ Next.js Front  │  FastAPI Backend  │
│ (opsai-ui)     │  (opsai-api)      │
└───────────────┴──────────────────┘
         │                  │
         ▼                  ▼
  ┌───────────┐    ┌─────────────┐
  │ Neon Postgres│    │ Upstash Redis │
  └───────────┘    └─────────────┘
         │
         ▼
  ┌───────────┐
  │  Railway      │  ← Celery Workers
  │  (workers)    │
  └───────────┘
```

---

## Estimated Free-Tier Cost

| Service | Free Tier |
|---------|----------|
| Vercel Frontend | ✅ Free (unlimited hobby) |
| Vercel Backend | ✅ Free (100GB-hrs/mo) |
| Neon PostgreSQL | ✅ Free (0.5GB storage) |
| Upstash Redis | ✅ Free (10K commands/day) |
| Railway Worker | ⚠️ $5 credit/mo then $5/mo |

**Total: ~$0 to start, $5/mo at scale**
