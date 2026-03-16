import math
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.pipeline import LogAnalysis, PipelineRun
from app.models.user import User
from app.schemas.pipeline import LogAnalysisResponse, PipelineRunResponse

router = APIRouter()


class PagedRunResponse:
    pass  # replaced inline below for simplicity


@router.get("/project/{project_id}")
async def list_runs(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """List pipeline runs for a project with offset pagination."""
    offset = (page - 1) * limit
    base_q = (
        select(PipelineRun)
        .where(PipelineRun.project_id == project_id)
        .order_by(PipelineRun.created_at.desc())
    )

    total_result = await db.execute(
        select(func.count()).select_from(base_q.subquery())
    )
    total = total_result.scalar_one()

    data_result = await db.execute(base_q.offset(offset).limit(limit))
    items = data_result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": math.ceil(total / limit) if limit else 1,
        "limit": limit,
    }


@router.get("/{run_id}", response_model=PipelineRunResponse)
async def get_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(PipelineRun).where(PipelineRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


@router.get("/{run_id}/analysis", response_model=LogAnalysisResponse)
async def get_analysis(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(LogAnalysis).where(LogAnalysis.run_id == run_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or still processing.")
    return analysis
