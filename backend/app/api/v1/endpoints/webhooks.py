from fastapi import APIRouter, Request, HTTPException, Header, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_github_signature
from app.models.project import Project
from app.models.pipeline import PipelineRun, RunStatus
from app.workers.tasks import analyze_pipeline_run
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/github/{project_id}")
async def github_webhook(
    project_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()

    # Fetch project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Verify signature
    if project.webhook_secret and not verify_github_signature(body, x_hub_signature_256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "")

    if event_type == "workflow_run":
        workflow_run = payload.get("workflow_run", {})
        conclusion = workflow_run.get("conclusion")

        if conclusion == "failure":
            run = PipelineRun(
                project_id=project.id,
                external_run_id=str(workflow_run.get("id")),
                pipeline_name=workflow_run.get("name"),
                branch=workflow_run.get("head_branch"),
                commit_sha=workflow_run.get("head_sha"),
                commit_message=workflow_run.get("head_commit", {}).get("message"),
                status=RunStatus.FAILED,
                started_at=datetime.fromisoformat(workflow_run["run_started_at"].replace("Z", "+00:00")) if workflow_run.get("run_started_at") else None,
                finished_at=datetime.utcnow(),
                raw_log_url=workflow_run.get("logs_url"),
            )
            db.add(run)
            await db.commit()
            await db.refresh(run)

            # Enqueue AI analysis
            analyze_pipeline_run.delay(str(run.id))
            logger.info(f"Queued analysis for run {run.id}")

    return {"status": "received"}
