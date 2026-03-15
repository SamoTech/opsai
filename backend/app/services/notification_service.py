import logging
from typing import Optional
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.slack = AsyncWebClient(token=settings.SLACK_BOT_TOKEN) if settings.SLACK_BOT_TOKEN else None

    async def send_slack_alert(
        self,
        channel: str,
        pipeline_name: str,
        branch: str,
        root_cause: str,
        fix_suggestion: str,
        confidence: float,
        run_id: str,
    ) -> bool:
        if not self.slack:
            logger.warning("Slack not configured, skipping notification.")
            return False

        confidence_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.5 else "🔴"

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🚨 Pipeline Failed: {pipeline_name}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Branch:* `{branch}`"},
                    {"type": "mrkdwn", "text": f"*Confidence:* {confidence_emoji} {int(confidence * 100)}%"},
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Root Cause:*\n{root_cause}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*💡 Fix Suggestion:*\n{fix_suggestion}"}
            },
            {
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Full Analysis"},
                    "url": f"{settings.ALLOWED_ORIGINS[0]}/runs/{run_id}",
                    "style": "primary"
                }]
            }
        ]

        try:
            await self.slack.chat_postMessage(channel=channel, blocks=blocks)
            return True
        except SlackApiError as e:
            logger.error(f"Slack notification failed: {e}")
            return False


notification_service = NotificationService()
