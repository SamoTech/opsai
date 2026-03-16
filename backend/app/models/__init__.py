# Import ALL models here so they register with Base.metadata.
# Alembic's env.py imports this module once and detects every table.
# Add new model files to this list as the project grows.

from app.models.user import User                   # noqa: F401
from app.models.project import Project             # noqa: F401
from app.models.pipeline import PipelineRun, LogAnalysis  # noqa: F401
from app.models.api_key import APIKey              # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.team import Team, TeamMember       # noqa: F401

__all__ = [
    "User",
    "Project",
    "PipelineRun",
    "LogAnalysis",
    "APIKey",
    "Subscription",
    "Team",
    "TeamMember",
]
