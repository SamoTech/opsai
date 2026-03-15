from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.pipeline import PipelineRun, LogAnalysis
from app.schemas.pipeline import PipelineRunResponse, LogAnalysisResponse
from typing import List
from uuid import UUID

router = APIRouter()


@router.get("/project/{project_id}", response_model=List[PipelineRunResponse])
async def list_runs(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PipelineRun)
        .where(PipelineRun.project_id == project_id)
        .order_by(PipelineRun.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()


@router.get("/{run_id}", response_model=PipelineRunResponse)
async def get_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PipelineRun).where(PipelineRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


@router.get("/{run_id}/analysis", response_model=LogAnalysisResponse)
async def get_analysis(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LogAnalysis).where(LogAnalysis.run_id == run_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or still processing.")
    return analysis
