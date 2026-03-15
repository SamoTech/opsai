import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.api_key import APIKey
from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

router = APIRouter()


class APIKeyCreate(BaseModel):
    name: str
    user_id: UUID


class APIKeyResponse(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: datetime | None
    requests_count: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=dict)
async def create_api_key(payload: APIKeyCreate, db: AsyncSession = Depends(get_db)):
    raw_key = f"opsai_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12]

    api_key = APIKey(
        user_id=payload.user_id,
        name=payload.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
    )
    db.add(api_key)
    await db.commit()

    # Return full key ONCE — never stored in plaintext
    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "key": raw_key,  # shown only once
        "key_prefix": key_prefix,
        "message": "Save this key securely. It will not be shown again."
    }


@router.get("/user/{user_id}", response_model=List[APIKeyResponse])
async def list_api_keys(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(APIKey).where(APIKey.user_id == user_id, APIKey.is_active == True))
    return result.scalars().all()


@router.delete("/{key_id}")
async def revoke_api_key(key_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found.")
    key.is_active = False
    await db.commit()
    return {"message": "API key revoked."}
