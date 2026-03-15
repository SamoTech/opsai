# OpsAI Deployment Guide

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+
- Groq API key (free tier available)

## Quick Deploy (Docker Compose)

```bash
git clone https://github.com/SamoTech/opsai.git
cd opsai
cp .env.example .env
# Edit .env with your keys
nano .env
docker-compose up -d
```

## Environment Setup

### Required Variables

| Variable | Description |
|---|---|
| `APP_SECRET_KEY` | JWT signing secret (use `openssl rand -hex 32`) |
| `DATABASE_URL` | PostgreSQL connection string |
| `GROQ_API_KEY` | Get free key at console.groq.com |
| `GITHUB_WEBHOOK_SECRET` | Random string for webhook verification |

### Optional (Notifications)

| Variable | Description |
|---|---|
| `SLACK_BOT_TOKEN` | Slack bot token for alerts |
| `SMTP_*` | Email configuration for alerts |

## GitHub Actions Integration

1. Create a project in OpsAI dashboard
2. Copy the generated webhook URL: `https://your-domain.com/api/v1/webhooks/github/{project_id}`
3. Go to your GitHub repo → Settings → Webhooks → Add webhook
4. Set Content-Type: `application/json`
5. Select event: **Workflow runs**
6. Paste your webhook secret

## Production with Nginx

```nginx
server {
    listen 80;
    server_name opsai.yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

## Database Migrations

```bash
# Run inside backend container
docker compose exec backend alembic upgrade head
```

## Scaling

```bash
# Scale Celery workers
docker compose up -d --scale worker=4
```
