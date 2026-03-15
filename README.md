# 🤖 OpsAI — AI-Powered DevOps Copilot

> Analyze CI/CD failures, identify root causes, and get AI-generated fix suggestions — automatically.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Next.js](https://img.shields.io/badge/frontend-Next.js_14-black.svg)

## 🚀 What is OpsAI?

OpsAI is a developer tool that connects to your CI/CD pipelines and uses LLM intelligence to:

- 🔍 **Analyze** failed pipeline logs automatically
- 🧠 **Classify** root causes (dependency, config, code, infra)
- 💡 **Suggest** actionable fixes with code snippets
- 📊 **Dashboard** pipeline health, MTTR, and failure trends
- 🔔 **Alert** via Slack or email with AI-generated summaries

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│              OpsAI Platform             │
├──────────────┬──────────────────────────┤
│   Frontend   │  Next.js 14 + Tailwind   │
├──────────────┼──────────────────────────┤
│   API Layer  │  FastAPI (Python 3.11)   │
├──────────────┼──────────────────────────┤
│  AI Engine   │  LangChain + Groq LLM    │
├──────────────┼──────────────────────────┤
│   Database   │  PostgreSQL + Redis      │
└──────────────┴──────────────────────────┘
```

## 📦 Quick Start

```bash
# Clone the repository
git clone https://github.com/SamoTech/opsai.git
cd opsai

# Start with Docker Compose
cp .env.example .env
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
opsai/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Config, security, DB
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic + AI
│   │   └── workers/  # Celery async tasks
│   ├── tests/
│   └── Dockerfile
├── frontend/         # Next.js 14 app
│   ├── src/
│   │   ├── app/      # App router pages
│   │   ├── components/
│   │   └── lib/
│   └── Dockerfile
├── database/         # Migrations & seeds
├── docker/           # Docker configs
├── scripts/          # Utility scripts
├── docs/             # Documentation
└── .github/workflows # CI/CD pipelines
```

## 🔗 Integrations

- GitHub Actions
- GitLab CI
- Jenkins
- Slack notifications
- Email alerts

## 📄 License

MIT © [SamoTech](https://github.com/SamoTech)
