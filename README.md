<div align="center">

<img src="https://img.shields.io/badge/OpsAI-DevOps%20Copilot-blue?style=for-the-badge&logo=robot&logoColor=white" alt="OpsAI" />

# 🤖 OpsAI

### AI-Powered DevOps Copilot

**Analyze CI/CD failures. Identify root causes. Get AI-generated fixes. Automatically.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20OpenAI%20%7C%20Anthropic-orange?style=flat-square)](https://console.groq.com)
[![Deploy on Vercel](https://img.shields.io/badge/Deploy-Vercel-black?style=flat-square&logo=vercel)](https://vercel.com)
[![GitHub Stars](https://img.shields.io/github/stars/SamoTech/opsai?style=flat-square&color=yellow)](https://github.com/SamoTech/opsai/stargazers)

[**Report Bug**](https://github.com/SamoTech/opsai/issues) · [**Request Feature**](https://github.com/SamoTech/opsai/issues) · [**Discussions**](https://github.com/SamoTech/opsai/discussions)

</div>

---

## ✨ What is OpsAI?

OpsAI is an open-source DevOps intelligence platform that connects to your CI/CD pipelines and uses Large Language Models to **automatically diagnose failures and suggest fixes** — before you even open the logs.

When your pipeline fails, OpsAI:

1. 🔍 **Receives** the failure event via webhook
2. 🧠 **Analyzes** the full log with LLM intelligence
3. 🎯 **Classifies** the root cause into 7 categories
4. 💡 **Suggests** a specific, actionable fix with code snippet
5. 💬 **Comments** the fix directly on your GitHub PR
6. 🔧 **Opens** an auto-fix Pull Request (optional)
7. 🔔 **Alerts** your team on Slack with an AI summary
8. 📊 **Tracks** reliability trends and recurring failures

---

## 🚀 Features

### 🤖 AI Engine
- **Multi-LLM support** — Groq (default, free), OpenAI GPT-4o, Anthropic Claude, Ollama (local)
- **7 root cause categories**: dependency, configuration, code error, infrastructure, timeout, permission, unknown
- **Automatic fallback** — if primary LLM fails, falls back to Groq
- **Confidence scoring** — 0–100% confidence on every analysis

### 🔗 CI/CD Integrations
- ✅ **GitHub Actions** — webhook + auto PR comments + auto-fix PRs
- ✅ **GitLab CI** — Pipeline Hook integration
- ✅ **Jenkins** — build notification integration
- 🚧 Bitbucket Pipelines *(coming in v1.1)*

### 📊 Dashboard & Analytics
- Real-time pipeline health dashboard
- **WebSocket live updates** — no page refresh needed
- Failure trend heatmap and MTTR tracking
- **Recurring failure detection** — alerts when same error repeats 3+ times
- **Reliability score** (0–100) per project with embeddable README badge

### 🔔 Notifications
- Rich **Slack** block messages with fix suggestion
- **Email** alerts via SMTP
- **Browser push notifications** on analysis complete
- GitHub PR review comments with full analysis

### 💳 SaaS & Teams
- **Stripe billing** — Free / Pro ($29/mo) / Team ($99/mo)
- **Team workspaces** with Owner / Admin / Viewer roles
- **SSO** via Google OAuth + GitHub OAuth
- **API keys** with SHA-256 hashing, rate limiting, usage tracking
- Public REST API + Python & JavaScript SDKs

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│                  OpsAI Platform                  │
├───────────────┬────────────────────────────────────┤
│   Frontend    │  Next.js 14 + Tailwind + React Query  │
├───────────────┼────────────────────────────────────┤
│   API Layer   │  FastAPI + WebSocket (Python 3.11)     │
├───────────────┼────────────────────────────────────┤
│  AI Engine    │  LangChain + Groq / OpenAI / Anthropic │
├───────────────┼────────────────────────────────────┤
│  Task Queue   │  Celery + Redis (async processing)     │
├───────────────┼────────────────────────────────────┤
│   Database    │  PostgreSQL + Redis cache              │
└───────────────┴────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Option A — Docker Compose (Recommended)

```bash
git clone https://github.com/SamoTech/opsai.git
cd opsai
cp .env.example .env
# Add your GROQ_API_KEY to .env
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

### Option B — Vercel (Zero Config)

See the full guide: [**docs/VERCEL_DEPLOYMENT.md**](docs/VERCEL_DEPLOYMENT.md)

```
Frontend → Vercel (Next.js)        → Free
Backend  → Vercel (FastAPI)        → Free
Database → Neon PostgreSQL         → Free
Redis    → Upstash                 → Free
Workers  → Railway                 → ~$5/mo
```

---

## 📁 Project Structure

```
opsai/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   ← auth, projects, webhooks, runs,
│   │   │                        billing, api_keys, analytics,
│   │   │                        teams, websocket
│   │   ├── core/               ← config, database, security
│   │   ├── models/             ← user, project, pipeline,
│   │   │                        api_key, subscription, team
│   │   ├── services/           ← ai_engine, llm_factory,
│   │   │                        github_service, stripe_service,
│   │   │                        pattern_service, notification,
│   │   │                        reliability_badge
│   │   └── workers/            ← celery tasks (async AI analysis)
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                ← dashboard, projects, runs,
│   │   │                        billing, api-keys, team
│   │   ├── components/         ← Sidebar, DashboardStats,
│   │   │                        RecentRuns
│   │   ├── hooks/              ← useRealtimeRuns (WebSocket)
│   │   └── lib/                ← axios API client
│   └── Dockerfile
├── database/migrations/        ← Alembic
├── docker-compose.yml
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              ← test + lint + build on every PR
│   │   └── deploy.yml          ← auto-deploy to VPS on main push
│   └── FUNDING.yml
├── docs/
│   ├── DEPLOYMENT.md
│   ├── VERCEL_DEPLOYMENT.md
│   ├── SECURITY.md
│   └── ROADMAP.md
├── .env.example
├── README.md
└── LICENSE
```

---

## 🔌 API Reference

Full interactive docs available at `/docs` (Swagger UI) after starting the backend.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/login` | Login + get JWT |
| `POST` | `/api/v1/projects/` | Create project |
| `POST` | `/api/v1/webhooks/github/{id}` | GitHub Actions webhook |
| `POST` | `/api/v1/webhooks/gitlab/{id}` | GitLab CI webhook |
| `POST` | `/api/v1/webhooks/jenkins/{id}` | Jenkins webhook |
| `GET` | `/api/v1/runs/{run_id}/analysis` | Get AI analysis |
| `GET` | `/api/v1/analytics/projects/{id}/patterns` | Failure patterns |
| `GET` | `/api/v1/analytics/badge/{id}` | Reliability SVG badge |
| `GET` | `/api/v1/billing/plans` | Subscription plans |
| `POST` | `/api/v1/billing/checkout` | Create Stripe checkout |
| `WS` | `/api/v1/ws/projects/{id}` | Real-time WebSocket |

### SDK Usage

```python
# Python
pip install opsai-sdk

import opsai
client = opsai.Client(api_key="opsai_xxxx")
result = client.analyze(log_text=open("build.log").read())
print(result.fix_suggestion)   # "Run: npm install --legacy-peer-deps"
print(result.confidence)       # 0.95
```

```javascript
// JavaScript
npm install @opsai/sdk

import { OpsAI } from '@opsai/sdk';
const client = new OpsAI({ apiKey: 'opsai_xxxx' });
const result = await client.analyze({ log: buildLog });
console.log(result.fixSuggestion);
```

---

## 💳 Pricing

| Plan | Price | Runs/mo | Projects | Features |
|------|-------|---------|----------|---------|
| **Free** | $0 | 50 | 3 | Core analysis, Slack alerts |
| **Pro** | $29/mo | 1,000 | Unlimited | Auto-fix PRs, PR comments, pattern insights |
| **Team** | $99/mo | 10,000 | Unlimited | SSO, team workspaces, reliability reports |
| **Enterprise** | Custom | Unlimited | Unlimited | On-premise, SLA, dedicated support |

---

## 🛡️ Security

- 🔐 JWT authentication with bcrypt password hashing
- 🖊️ HMAC-SHA256 webhook signature verification
- 🔑 API keys stored as SHA-256 hashes (never plaintext)
- 🚧 Non-root Docker containers
- 🔒 CORS restricted to configured origins
- 📦 All secrets via environment variables

See [**docs/SECURITY.md**](docs/SECURITY.md) for full security guide.

---

## 🧪 Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
# 1. Fork the repo
# 2. Create your branch
git checkout -b feat/amazing-feature

# 3. Commit your changes
git commit -m 'feat: add amazing feature'

# 4. Push and open a PR
git push origin feat/amazing-feature
```

---

## 📞 Support

- 🐛 [Open an Issue](https://github.com/SamoTech/opsai/issues)
- 💬 [Discussions](https://github.com/SamoTech/opsai/discussions)
- 📧 [samo.hossam@gmail.com](mailto:samo.hossam@gmail.com)
- 🐦 Twitter: [@OssamaHashim](https://twitter.com/OssamaHashim)

---

## 🗃️ Roadmap

- [x] GitHub Actions integration
- [x] GitLab CI + Jenkins integration
- [x] AI log analysis (Groq / OpenAI / Anthropic / Ollama)
- [x] Auto-fix Pull Requests
- [x] GitHub PR comment bot
- [x] Real-time WebSocket dashboard
- [x] Stripe billing (Free / Pro / Team)
- [x] Team workspaces + SSO
- [x] Reliability score + README badge
- [x] Public API + Python & JS SDKs
- [ ] Bitbucket Pipelines
- [ ] Mobile app
- [ ] GitHub Marketplace listing

See the full [**ROADMAP.md**](docs/ROADMAP.md).

---

## ⭐ Star History

If OpsAI saves you time, please consider giving it a star — it helps more developers find the project!

[![Star History Chart](https://api.star-history.com/svg?repos=SamoTech/opsai&type=Date)](https://star-history.com/#SamoTech/opsai&Date)

---

<div align="center">

Made with ❤️ by [Ossama Hashim](https://github.com/SamoTech) · [SamoTech](https://github.com/SamoTech)

[![Twitter](https://img.shields.io/twitter/follow/OssamaHashim?style=social)](https://twitter.com/OssamaHashim)
[![GitHub](https://img.shields.io/github/followers/SamoTech?style=social)](https://github.com/SamoTech)

</div>
