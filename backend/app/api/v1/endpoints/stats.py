from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.pipeline import LogAnalysis, PipelineRun, RunStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.stats import AnalysisStats, DashboardStats, ProjectStats, RunStats

router = APIRouter()


@router.get("/", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregated dashboard statistics for the authenticated user."""

    # ── Projects ────────────────────────────────────────────────────────────
    total_projects_q = await db.execute(
        select(func.count(Project.id)).where(Project.owner_id == current_user.id)
    )
    total_projects = total_projects_q.scalar_one() or 0

    active_projects_q = await db.execute(
        select(func.count(Project.id)).where(
            Project.owner_id == current_user.id,
            Project.is_active == True,
        )
    )
    active_projects = active_projects_q.scalar_one() or 0

    # ── Runs ───────────────────────────────────────────────────────────────────
    user_project_ids = select(Project.id).where(Project.owner_id == current_user.id)

    total_runs_q = await db.execute(
        select(func.count(PipelineRun.id)).where(
            PipelineRun.project_id.in_(user_project_ids)
        )
    )
    total_runs = total_runs_q.scalar_one() or 0

    failed_runs_q = await db.execute(
        select(func.count(PipelineRun.id)).where(
            PipelineRun.project_id.in_(user_project_ids),
            PipelineRun.status == RunStatus.FAILED,
        )
    )
    failed_runs = failed_runs_q.scalar_one() or 0

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_runs_q = await db.execute(
        select(func.count(PipelineRun.id)).where(
            PipelineRun.project_id.in_(user_project_ids),
            PipelineRun.created_at >= seven_days_ago,
        )
    )
    recent_runs_7d = recent_runs_q.scalar_one() or 0

    # ── Analyses ───────────────────────────────────────────────────────────
    user_run_ids = select(PipelineRun.id).where(
        PipelineRun.project_id.in_(user_project_ids)
    )

    analysis_q = await db.execute(
        select(
            func.count(LogAnalysis.id),
            func.coalesce(func.avg(LogAnalysis.confidence_score), 0.0),
        ).where(LogAnalysis.run_id.in_(user_run_ids))
    )
    total_analyses, avg_confidence = analysis_q.one()
    total_analyses = total_analyses or 0
    avg_confidence = float(avg_confidence or 0.0)

    return DashboardStats(
        projects=ProjectStats(
            total_projects=total_projects,
            active_projects=active_projects,
        ),
        runs=RunStats(
            total_runs=total_runs,
            failed_runs=failed_runs,
            recent_runs_7d=recent_runs_7d,
        ),
        analyses=AnalysisStats(
            total_analyses=total_analyses,
            avg_confidence=round(avg_confidence, 4),
        ),
    )
