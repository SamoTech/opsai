from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.team import Team, TeamMember, TeamRole
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID
import re

router = APIRouter()


class TeamCreate(BaseModel):
    name: str
    owner_user_id: UUID


class InviteMember(BaseModel):
    email: EmailStr
    role: TeamRole = TeamRole.VIEWER


class TeamResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(payload: TeamCreate, db: AsyncSession = Depends(get_db)):
    slug = re.sub(r"[^a-z0-9-]", "-", payload.name.lower().strip())
    team = Team(name=payload.name, slug=slug)
    db.add(team)
    await db.flush()

    member = TeamMember(team_id=team.id, user_id=payload.owner_user_id, role=TeamRole.OWNER)
    db.add(member)
    await db.commit()
    await db.refresh(team)
    return team


@router.get("/{team_id}/members")
async def list_members(team_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id)
    )
    members = result.scalars().all()
    return [{"user_id": str(m.user_id), "role": m.role, "joined_at": m.joined_at} for m in members]


@router.post("/{team_id}/invite")
async def invite_member(team_id: UUID, payload: InviteMember, db: AsyncSession = Depends(get_db)):
    from app.models.user import User
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. They must register first.")

    existing = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already in team.")

    member = TeamMember(team_id=team_id, user_id=user.id, role=payload.role)
    db.add(member)
    await db.commit()
    return {"message": f"{payload.email} added to team with role {payload.role}"}
