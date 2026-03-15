from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.pattern_service import pattern_service
from app.services.reliability_badge import generate_badge_svg
from uuid import UUID

router = APIRouter()


@router.get("/projects/{project_id}/patterns")
async def get_patterns(project_id: UUID, days: int = 30, db: AsyncSession = Depends(get_db)):
    return await pattern_service.get_project_patterns(db, str(project_id), days)


@router.get("/projects/{project_id}/reliability")
async def get_reliability_score(project_id: UUID, db: AsyncSession = Depends(get_db)):
    patterns = await pattern_service.get_project_patterns(db, str(project_id))
    return {
        "project_id": str(project_id),
        "reliability_score": patterns["reliability_score"],
        "success_rate": patterns["success_rate"],
        "mttr_seconds": patterns["mttr_seconds"],
        "recurring_failures": len(patterns["recurring_failures"]),
    }


@router.get("/badge/{project_id}", response_class=Response)
async def get_reliability_badge(project_id: UUID, db: AsyncSession = Depends(get_db)):
    patterns = await pattern_service.get_project_patterns(db, str(project_id))
    svg = generate_badge_svg(patterns["reliability_score"])
    return Response(content=svg, media_type="image/svg+xml", headers={
        "Cache-Control": "max-age=300",
    })
