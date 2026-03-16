import logging
from typing import Optional

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.slack = AsyncWebClient(token=settings.SLACK_BOT_TOKEN) if getattr(settings, 'SLACK_BOT_TOKEN', None) else None

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
        frontend_url = getattr(settings, 'ALLOWED_ORIGINS', ['http://localhost:3000'])[0]

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
                    "url": f"{frontend_url}/runs/{run_id}",
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

    async def send_email(
        self,
        to_email: str,
        pipeline_name: str,
        branch: str,
        root_cause: str,
        fix_suggestion: str,
        confidence: float,
        run_url: str,
    ) -> bool:
        """Fix 14: Send email alert via aiosmtplib (async SMTP).

        Requires SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
        to be present in settings. Silently skips if not configured.
        """
        smtp_host = getattr(settings, 'SMTP_HOST', None)
        smtp_user = getattr(settings, 'SMTP_USER', None)
        smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        smtp_from = getattr(settings, 'SMTP_FROM', smtp_user)
        smtp_port = int(getattr(settings, 'SMTP_PORT', 587))

        if not smtp_host or not smtp_user:
            logger.debug("SMTP not configured, skipping email notification.")
            return False

        confidence_pct = int(confidence * 100)
        subject = f"[OpsAI] Pipeline Failed: {pipeline_name} ({branch})"

        html_body = f"""
        <h2>🚨 Pipeline Failure Detected</h2>
        <table>
          <tr><td><b>Pipeline</b></td><td>{pipeline_name}</td></tr>
          <tr><td><b>Branch</b></td><td><code>{branch}</code></td></tr>
          <tr><td><b>Confidence</b></td><td>{confidence_pct}%</td></tr>
        </table>
        <h3>Root Cause</h3>
        <p>{root_cause}</p>
        <h3>💡 Fix Suggestion</h3>
        <p>{fix_suggestion}</p>
        <p><a href="{run_url}">View Full Analysis →</a></p>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                start_tls=True,
            )
            logger.info(f"Email sent to {to_email} for pipeline {pipeline_name}")
            return True
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False


notification_service = NotificationService()
