from pydantic import BaseModel


class ProjectStats(BaseModel):
    total_projects: int
    active_projects: int


class RunStats(BaseModel):
    total_runs: int
    failed_runs: int
    recent_runs_7d: int


class AnalysisStats(BaseModel):
    total_analyses: int
    avg_confidence: float


class DashboardStats(BaseModel):
    projects: ProjectStats
    runs: RunStats
    analyses: AnalysisStats
