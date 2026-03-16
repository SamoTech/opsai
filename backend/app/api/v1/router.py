from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, webhooks, runs, billing, api_keys, analytics, teams
from app.api.v1.endpoints.websocket import router as ws_router
from app.api.v1.endpoints import stats, oauth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(oauth.router, prefix="/auth/oauth", tags=["OAuth"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(runs.router, prefix="/runs", tags=["Pipeline Runs"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])
api_router.include_router(ws_router, tags=["WebSocket"])
