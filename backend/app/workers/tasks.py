import asyncio
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.ai_engine import ai_engine
from app.services.notification_service import notification_service
from app.models.pipeline import PipelineRun, LogAnalysis, RunStatus, RootCauseCategory
from sqlalchemy import select
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def analyze_pipeline_run(self, run_id: str):
    """Async Celery task: analyze a failed pipeline run log with AI."""
    try:
        asyncio.get_event_loop().run_until_complete(_analyze_run(run_id))
    except Exception as exc:
        logger.error(f"Task failed for run {run_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


async def _analyze_run(run_id: str):
    async with AsyncSessionLocal() as db:
        # Fetch run
        result = await db.execute(select(PipelineRun).where(PipelineRun.id == run_id))
        run = result.scalar_one_or_none()
        if not run or not run.raw_log_text:
            logger.warning(f"Run {run_id} not found or has no log.")
            return

        # Fetch project for notification config
        from app.models.project import Project
        proj_result = await db.execute(select(Project).where(Project.id == run.project_id))
        project = proj_result.scalar_one_or_none()

        # Run AI analysis
        analysis_data = await ai_engine.analyze_log(run.raw_log_text, run.pipeline_name)

        # Persist analysis
        analysis = LogAnalysis(
            run_id=run.id,
            root_cause_category=RootCauseCategory(analysis_data.get("root_cause_category", "unknown")),
            root_cause_summary=analysis_data.get("root_cause_summary"),
            error_snippet=analysis_data.get("error_snippet"),
            fix_suggestion=analysis_data.get("fix_suggestion"),
            fix_code_snippet=analysis_data.get("fix_code_snippet"),
            confidence_score=float(analysis_data.get("confidence_score", 0.0)),
            llm_provider=analysis_data.get("llm_provider"),
            llm_model=analysis_data.get("llm_model"),
            tokens_used=analysis_data.get("tokens_used", 0),
            raw_llm_response=analysis_data,
        )
        db.add(analysis)
        await db.commit()

        # Send Slack notification if configured
        if project and project.slack_channel and analysis.root_cause_summary:
            await notification_service.send_slack_alert(
                channel=project.slack_channel,
                pipeline_name=run.pipeline_name or "Unknown Pipeline",
                branch=run.branch or "unknown",
                root_cause=analysis.root_cause_summary,
                fix_suggestion=analysis.fix_suggestion or "No suggestion available.",
                confidence=analysis.confidence_score,
                run_id=str(run.id),
            )

        logger.info(f"Analysis complete for run {run_id}")
