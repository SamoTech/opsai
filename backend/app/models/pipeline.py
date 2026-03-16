from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SAEnum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum
from app.core.database import Base


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RootCauseCategory(str, enum.Enum):
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    CODE_ERROR = "code_error"
    INFRASTRUCTURE = "infrastructure"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    external_run_id = Column(String(255))  # GitHub Actions / GitLab / Jenkins run ID
    pipeline_name = Column(String(255))
    branch = Column(String(255))
    commit_sha = Column(String(40))
    commit_message = Column(Text)
    status = Column(SAEnum(RunStatus), default=RunStatus.PENDING)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    duration_seconds = Column(Integer)
    raw_log_url = Column(String(500))
    raw_log_text = Column(Text)
    # Fix 6: fields required by tasks.py for PR comments and auto-fix PRs
    repo_full_name = Column(String(255), nullable=True)  # e.g. "owner/repo"
    pr_number = Column(Integer, nullable=True)           # GitHub PR number
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="pipeline_runs")
    analysis = relationship("LogAnalysis", back_populates="run", uselist=False, cascade="all, delete-orphan")


class LogAnalysis(Base):
    __tablename__ = "log_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_runs.id"), nullable=False)
    root_cause_category = Column(SAEnum(RootCauseCategory), default=RootCauseCategory.UNKNOWN)
    root_cause_summary = Column(Text)
    error_snippet = Column(Text)
    fix_suggestion = Column(Text)
    fix_code_snippet = Column(Text)
    confidence_score = Column(Float, default=0.0)
    llm_provider = Column(String(50))
    llm_model = Column(String(100))
    tokens_used = Column(Integer, default=0)
    raw_llm_response = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("PipelineRun", back_populates="analysis")
