import asyncio
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.ai_engine import ai_engine
from app.services.notification_service import notification_service
from app.services.github_service import github_service
from app.models.pipeline import PipelineRun, LogAnalysis, RunStatus, RootCauseCategory
from app.models.project import Project
from sqlalchemy import select
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def analyze_pipeline_run(self, run_id: str):
    try:
        asyncio.get_event_loop().run_until_complete(_analyze_run(run_id))
    except Exception as exc:
        logger.error(f"Task failed for run {run_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


async def _analyze_run(run_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineRun).where(PipelineRun.id == run_id))
        run = result.scalar_one_or_none()
        if not run or not run.raw_log_text:
            logger.warning(f"Run {run_id} not found or has no log.")
            return

        proj_result = await db.execute(select(Project).where(Project.id == run.project_id))
        project = proj_result.scalar_one_or_none()

        # Use project-level LLM config if set
        llm_provider = getattr(project, 'llm_provider', None) if project else None
        llm_model = getattr(project, 'llm_model', None) if project else None

        from app.services.ai_engine import AIEngine
        engine = AIEngine(provider=llm_provider, model=llm_model)
        analysis_data = await engine.analyze_log(run.raw_log_text, run.pipeline_name)

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
        await db.refresh(analysis)

        # ─ WebSocket broadcast
        try:
            from app.api.v1.endpoints.websocket import broadcast_to_project
            await broadcast_to_project(str(run.project_id), {
                "type": "analysis_complete",
                "run_id": str(run.id),
                "status": "failed",
                "root_cause": analysis.root_cause_category.value,
                "confidence": analysis.confidence_score,
            })
        except Exception as e:
            logger.warning(f"WebSocket broadcast failed: {e}")

        # ─ Slack notification
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

        # ─ GitHub PR comment (if PR number and repo available)
        repo_full_name = getattr(run, 'repo_full_name', None)
        pr_number = getattr(run, 'pr_number', None)
        if repo_full_name and pr_number and getattr(project, 'pr_comments_enabled', False):
            await github_service.post_pr_comment(
                repo_full_name=repo_full_name,
                pr_number=int(pr_number),
                analysis=analysis_data,
                run_id=str(run.id),
            )

        # ─ Auto-fix PR (if enabled and confidence high enough)
        if repo_full_name and run.branch and analysis.confidence_score >= 0.75:
            if getattr(project, 'auto_fix_enabled', False):
                pr_url = await github_service.create_fix_pr(
                    repo_full_name=repo_full_name,
                    base_branch=run.branch,
                    analysis=analysis_data,
                    run_id=str(run.id),
                )
                if pr_url:
                    logger.info(f"Auto-fix PR created: {pr_url}")

        logger.info(f"Analysis complete for run {run_id}")
