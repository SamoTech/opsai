import secrets
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.project import Project
from app.models.user import User

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    repo_url: Optional[str] = None
    slack_channel: Optional[str] = None
    alert_email: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    repo_url: Optional[str]
    webhook_secret: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class PagedProjectResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    pages: int
    limit: int


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        repo_url=payload.repo_url,
        webhook_secret=secrets.token_hex(32),
        slack_channel=payload.slack_channel,
        alert_email=payload.alert_email,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/", response_model=PagedProjectResponse)
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    offset = (page - 1) * limit
    base_q = select(Project).where(
        Project.owner_id == current_user.id,
        Project.is_active == True,
    ).order_by(Project.created_at.desc())

    total_result = await db.execute(
        select(func.count()).select_from(base_q.subquery())
    )
    total = total_result.scalar_one()

    data_result = await db.execute(base_q.offset(offset).limit(limit))
    items = data_result.scalars().all()

    import math
    return PagedProjectResponse(
        items=items,
        total=total,
        page=page,
        pages=math.ceil(total / limit) if limit else 1,
        limit=limit,
    )
