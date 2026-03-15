from enum import Enum
from typing import Optional
from langchain_core.language_models import BaseChatModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


def get_llm(provider: Optional[str] = None, model: Optional[str] = None) -> BaseChatModel:
    """Factory: return the correct LangChain LLM based on provider."""
    provider = provider or settings.DEFAULT_LLM_PROVIDER
    model = model or settings.DEFAULT_LLM_MODEL

    if provider == LLMProvider.GROQ:
        from langchain_groq import ChatGroq
        return ChatGroq(api_key=settings.GROQ_API_KEY, model_name=model, temperature=0.1, max_tokens=2048)

    elif provider == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(api_key=settings.OPENAI_API_KEY, model=model, temperature=0.1, max_tokens=2048)

    elif provider == LLMProvider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(api_key=settings.ANTHROPIC_API_KEY, model=model, temperature=0.1, max_tokens=2048)

    elif provider == LLMProvider.OLLAMA:
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=model, temperature=0.1)

    else:
        logger.warning(f"Unknown provider '{provider}', falling back to Groq")
        from langchain_groq import ChatGroq
        return ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-70b-8192", temperature=0.1)
