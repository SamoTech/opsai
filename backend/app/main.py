from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.core.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_tables() is ONLY for local development without running Alembic.
    # In production (ENVIRONMENT=production) Alembic migrations run as a
    # pre-deploy step via the 'migrate' Docker Compose service.
    env = getattr(settings, "ENVIRONMENT", "development")
    if env not in ("production", "staging"):
        await create_tables()
    yield


app = FastAPI(
    title="OpsAI API",
    description="AI-Powered DevOps Copilot — Analyze, diagnose, and fix CI/CD failures.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Rate limiter ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Session middleware (required by Authlib OAuth state parameter) ────────────
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.APP_SECRET_KEY,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# allow_origins must be an explicit list (never "*") when allow_credentials=True
allowed_origins = getattr(settings, "ALLOWED_ORIGINS", ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "OpsAI", "version": "1.0.0"}
