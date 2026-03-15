from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.models.pipeline import PipelineRun, LogAnalysis, RunStatus
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import logging

logger = logging.getLogger(__name__)


class PatternService:
    async def get_project_patterns(self, db: AsyncSession, project_id: str, days: int = 30) -> dict:
        """Analyze failure patterns for a project over N days."""
        since = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(PipelineRun, LogAnalysis)
            .join(LogAnalysis, LogAnalysis.run_id == PipelineRun.id, isouter=True)
            .where(PipelineRun.project_id == project_id)
            .where(PipelineRun.created_at >= since)
            .order_by(PipelineRun.created_at.desc())
        )
        rows = result.all()

        total = len(rows)
        failed = sum(1 for r, _ in rows if r.status == RunStatus.FAILED)
        success = sum(1 for r, _ in rows if r.status == RunStatus.SUCCESS)

        # Category breakdown
        category_counts = defaultdict(int)
        fingerprints = defaultdict(list)

        for run, analysis in rows:
            if analysis:
                cat = analysis.root_cause_category.value if analysis.root_cause_category else "unknown"
                category_counts[cat] += 1
                if analysis.error_snippet:
                    fp = hashlib.md5(analysis.error_snippet[:200].encode()).hexdigest()[:8]
                    fingerprints[fp].append({
                        "run_id": str(run.id),
                        "category": cat,
                        "summary": analysis.root_cause_summary,
                        "date": run.created_at.isoformat(),
                    })

        # Detect recurring failures (same fingerprint 3+ times)
        recurring = [
            {
                "fingerprint": fp,
                "count": len(occurrences),
                "category": occurrences[0]["category"],
                "summary": occurrences[0]["summary"],
                "last_seen": occurrences[0]["date"],
            }
            for fp, occurrences in fingerprints.items()
            if len(occurrences) >= 3
        ]
        recurring.sort(key=lambda x: x["count"], reverse=True)

        # MTTR calculation
        mttr_seconds = None
        durations = [r.duration_seconds for r, _ in rows if r.duration_seconds]
        if durations:
            mttr_seconds = sum(durations) // len(durations)

        return {
            "period_days": days,
            "total_runs": total,
            "failed_runs": failed,
            "success_runs": success,
            "success_rate": round((success / total * 100), 1) if total else 0,
            "category_breakdown": dict(category_counts),
            "recurring_failures": recurring,
            "mttr_seconds": mttr_seconds,
            "reliability_score": self._calculate_score(total, failed, recurring, mttr_seconds),
        }

    def _calculate_score(self, total: int, failed: int, recurring: list, mttr: int | None) -> float:
        """Reliability score 0-100."""
        if total == 0:
            return 100.0
        success_rate = (total - failed) / total
        success_score = success_rate * 40

        mttr_score = 30.0
        if mttr:
            if mttr > 3600:
                mttr_score = 5
            elif mttr > 1800:
                mttr_score = 15
            elif mttr > 600:
                mttr_score = 22

        recurrence_penalty = min(len(recurring) * 5, 30)
        recurrence_score = 30 - recurrence_penalty

        return round(success_score + mttr_score + recurrence_score, 1)


pattern_service = PatternService()
