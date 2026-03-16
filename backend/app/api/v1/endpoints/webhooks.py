from datetime import datetime
from typing import Callable

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import verify_github_signature
from app.models.pipeline import PipelineRun, RunStatus
from app.models.project import Project
from app.workers.tasks import analyze_pipeline_run
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _webhook_key(request: Request) -> str:
    """Rate-limit key: per project_id, not per IP."""
    project_id = request.path_params.get("project_id", "unknown")
    return f"webhook:{project_id}"


# ─── GitHub Actions ───────────────────────────────────────────────────────────

@router.post("/github/{project_id}")
@limiter.limit("100/minute", key_func=_webhook_key)
async def github_webhook(
    project_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()
    project = await _get_project(db, project_id)
    if project.webhook_secret and not verify_github_signature(body, x_hub_signature_256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "")

    if event_type == "workflow_run" and payload.get("workflow_run", {}).get("conclusion") == "failure":
        wf = payload["workflow_run"]
        run = await _create_run(db, project.id, {
            "external_run_id": str(wf.get("id")),
            "pipeline_name": wf.get("name"),
            "branch": wf.get("head_branch"),
            "commit_sha": wf.get("head_sha"),
            "commit_message": wf.get("head_commit", {}).get("message"),
            "raw_log_url": wf.get("logs_url"),
            "pr_number": wf.get("pull_requests", [{}])[0].get("number") if wf.get("pull_requests") else None,
            "repo_full_name": payload.get("repository", {}).get("full_name"),
        })
        analyze_pipeline_run.delay(str(run.id))
    return {"status": "received"}


# ─── GitLab CI ────────────────────────────────────────────────────────────────

@router.post("/gitlab/{project_id}")
@limiter.limit("100/minute", key_func=_webhook_key)
async def gitlab_webhook(
    project_id: str,
    request: Request,
    x_gitlab_token: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project(db, project_id)
    if project.webhook_secret and x_gitlab_token != project.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid GitLab token.")

    payload = await request.json()
    event = request.headers.get("X-Gitlab-Event", "")

    if event == "Pipeline Hook" and payload.get("object_attributes", {}).get("status") == "failed":
        attrs = payload["object_attributes"]
        commit = payload.get("commit", {})
        run = await _create_run(db, project.id, {
            "external_run_id": str(attrs.get("id")),
            "pipeline_name": f"GitLab Pipeline #{attrs.get('id')}",
            "branch": attrs.get("ref"),
            "commit_sha": commit.get("id"),
            "commit_message": commit.get("message"),
        })
        analyze_pipeline_run.delay(str(run.id))
    return {"status": "received"}


# ─── Jenkins ──────────────────────────────────────────────────────────────────

@router.post("/jenkins/{project_id}")
@limiter.limit("100/minute", key_func=_webhook_key)
async def jenkins_webhook(
    project_id: str,
    request: Request,
    x_jenkins_token: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project(db, project_id)
    if project.webhook_secret and x_jenkins_token != project.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid Jenkins token.")

    payload = await request.json()
    build = payload.get("build", {})

    if build.get("phase") == "FINALIZED" and build.get("status") == "FAILURE":
        run = await _create_run(db, project.id, {
            "external_run_id": str(build.get("number")),
            "pipeline_name": payload.get("name", "Jenkins Build"),
            "branch": build.get("scm", {}).get("branch"),
            "commit_sha": build.get("scm", {}).get("commit"),
        })
        analyze_pipeline_run.delay(str(run.id))
    return {"status": "received"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _get_project(db: AsyncSession, project_id: str) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


async def _create_run(db: AsyncSession, project_id, data: dict) -> PipelineRun:
    run = PipelineRun(
        project_id=project_id,
        status=RunStatus.FAILED,
        started_at=datetime.utcnow(),
        **{k: v for k, v in data.items() if hasattr(PipelineRun, k)},
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run
