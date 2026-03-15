from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum
from app.core.database import Base


class IntegrationType(str, enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    JENKINS = "jenkins"


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repo_url = Column(String(500))
    integration_type = Column(SAEnum(IntegrationType), default=IntegrationType.GITHUB)
    webhook_secret = Column(String(255))
    slack_channel = Column(String(100))
    alert_email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    pipeline_runs = relationship("PipelineRun", back_populates="project", cascade="all, delete-orphan")
