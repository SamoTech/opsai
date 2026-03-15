from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.pipeline import RunStatus, RootCauseCategory


class PipelineRunResponse(BaseModel):
    id: UUID
    project_id: UUID
    pipeline_name: Optional[str]
    branch: Optional[str]
    commit_sha: Optional[str]
    commit_message: Optional[str]
    status: RunStatus
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class LogAnalysisResponse(BaseModel):
    id: UUID
    run_id: UUID
    root_cause_category: RootCauseCategory
    root_cause_summary: Optional[str]
    error_snippet: Optional[str]
    fix_suggestion: Optional[str]
    fix_code_snippet: Optional[str]
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookPayload(BaseModel):
    action: Optional[str]
    workflow_run: Optional[dict]
    repository: Optional[dict]
