from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.project import Project
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import secrets

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


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    # In production, extract user_id from JWT token
    from app.models.user import User
    result = await db.execute(select(User).limit(1))
    owner = result.scalar_one_or_none()
    if not owner:
        raise HTTPException(status_code=400, detail="No users found. Register first.")

    project = Project(
        owner_id=owner.id,
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


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.is_active == True))
    return result.scalars().all()
