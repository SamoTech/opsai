import pytest
from httpx import AsyncClient
from app.main import app


SAMPLE_GITHUB_PAYLOAD = {
    "action": "completed",
    "workflow_run": {
        "id": 12345678,
        "name": "CI",
        "head_branch": "main",
        "head_sha": "abc123def456",
        "conclusion": "failure",
        "run_started_at": "2026-03-15T00:00:00Z",
        "logs_url": "https://api.github.com/repos/owner/repo/actions/runs/12345678/logs",
        "head_commit": {"message": "fix: update deps"}
    },
    "repository": {"full_name": "owner/repo"}
}


@pytest.mark.asyncio
async def test_webhook_invalid_project():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhooks/github/00000000-0000-0000-0000-000000000000",
            json=SAMPLE_GITHUB_PAYLOAD,
            headers={"X-GitHub-Event": "workflow_run"}
        )
    assert response.status_code == 404
