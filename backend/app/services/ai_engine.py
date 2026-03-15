import json
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings
from app.services.llm_factory import get_llm
import logging

logger = logging.getLogger(__name__)

LOG_ANALYSIS_SYSTEM_PROMPT = """
You are an expert DevOps engineer and SRE specialist.
You analyze CI/CD pipeline failure logs and identify:
1. The root cause category (dependency, configuration, code_error, infrastructure, timeout, permission, unknown)
2. A concise root cause summary (1-2 sentences)
3. The exact error snippet from the log
4. A specific, actionable fix suggestion
5. A code/config snippet for the fix if applicable
6. A confidence score from 0.0 to 1.0

Respond ONLY with valid JSON in this exact format:
{
  "root_cause_category": "<category>",
  "root_cause_summary": "<summary>",
  "error_snippet": "<exact error line(s) from log>",
  "fix_suggestion": "<what to do to fix it>",
  "fix_code_snippet": "<code or config snippet or null>",
  "confidence_score": <0.0-1.0>
}
"""


class AIEngine:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model or settings.DEFAULT_LLM_MODEL
        self.llm = get_llm(self.provider, self.model)

    async def analyze_log(self, log_text: str, pipeline_name: Optional[str] = None) -> dict:
        truncated_log = log_text[-8000:] if len(log_text) > 8000 else log_text
        context = f"Pipeline: {pipeline_name}\n\n" if pipeline_name else ""
        user_message = f"{context}Failed CI/CD Log:\n\n```\n{truncated_log}\n```"

        messages = [
            SystemMessage(content=LOG_ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        # Try primary provider, fallback to Groq
        try:
            response = await self.llm.ainvoke(messages)
        except Exception as e:
            logger.warning(f"Primary LLM ({self.provider}) failed: {e}. Falling back to Groq.")
            from langchain_groq import ChatGroq
            fallback = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-70b-8192", temperature=0.1)
            response = await fallback.ainvoke(messages)

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            result = {
                "root_cause_category": "unknown",
                "root_cause_summary": "Could not parse AI response.",
                "error_snippet": "",
                "fix_suggestion": "Review the log manually.",
                "fix_code_snippet": None,
                "confidence_score": 0.0,
            }

        result["tokens_used"] = getattr(response, "usage_metadata", {}).get("total_tokens", 0)
        result["llm_model"] = self.model
        result["llm_provider"] = self.provider
        return result


ai_engine = AIEngine()
