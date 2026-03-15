from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, webhooks, runs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(runs.router, prefix="/runs", tags=["Pipeline Runs"])
