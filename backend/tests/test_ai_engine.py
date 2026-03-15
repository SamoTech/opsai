import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_engine import AIEngine


SAMPLE_LOG = """
Run npm install
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR! Found: react@18.2.0
npm ERR! Could not resolve dependency: peer react@"^17.0.0" from some-package@1.0.0
Process completed with exit code 1.
"""


@pytest.mark.asyncio
async def test_analyze_log_returns_structure():
    engine = AIEngine()

    mock_response = MagicMock()
    mock_response.content = '''{
        "root_cause_category": "dependency",
        "root_cause_summary": "Peer dependency conflict with React version.",
        "error_snippet": "npm ERR! ERESOLVE unable to resolve dependency tree",
        "fix_suggestion": "Use --legacy-peer-deps flag or upgrade the conflicting package.",
        "fix_code_snippet": "npm install --legacy-peer-deps",
        "confidence_score": 0.95
    }'''
    mock_response.usage_metadata = {"total_tokens": 250}

    with patch.object(engine.llm, 'ainvoke', new_callable=AsyncMock, return_value=mock_response):
        result = await engine.analyze_log(SAMPLE_LOG, "CI Build")

    assert result["root_cause_category"] == "dependency"
    assert result["confidence_score"] == 0.95
    assert "fix_suggestion" in result
    assert "error_snippet" in result


@pytest.mark.asyncio
async def test_analyze_log_handles_invalid_json():
    engine = AIEngine()

    mock_response = MagicMock()
    mock_response.content = "This is not valid JSON at all."
    mock_response.usage_metadata = {}

    with patch.object(engine.llm, 'ainvoke', new_callable=AsyncMock, return_value=mock_response):
        result = await engine.analyze_log(SAMPLE_LOG)

    assert result["root_cause_category"] == "unknown"
    assert result["confidence_score"] == 0.0
