"""
AI Provider Router — selects IBM Granite or Groq based on config and task type.
Never places raw API calls in agents — always routes through this module.
"""
import time
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import AIRequest

logger = get_logger(__name__)

# Task-to-provider mapping (deterministic, not LLM-decided)
TASK_PROVIDER_MAP = {
    "complaint_classification": "primary",
    "information_extraction": "primary",
    "routing_reasoning": "primary",
    "segregation_guidance": "primary",
    "summarization": "primary",
    "chat_response": "fast",        # conversational → Groq fast model
    "language_detection": "fast",
    "translation_assist": "fast",
}


class AIProviderRouter:
    """
    Routes AI requests to IBM Granite or Groq.
    Falls back to secondary provider on failure.
    Falls back to deterministic response if both fail.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self._ibm_provider = None
        self._groq_provider = None

    def _get_ibm_provider(self):
        if self._ibm_provider is None:
            from app.ai.providers.ibm_granite import IBMGraniteProvider
            self._ibm_provider = IBMGraniteProvider()
        return self._ibm_provider

    def _get_groq_provider(self):
        if self._groq_provider is None:
            from app.ai.providers.groq_provider import GroqProvider
            self._groq_provider = GroqProvider()
        return self._groq_provider

    def _resolve_provider(self, task: str) -> tuple[str, str]:
        """Returns (provider_name, model) for the given task."""
        assignment = TASK_PROVIDER_MAP.get(task, "primary")
        primary = settings.primary_llm_provider
        fallback = settings.fallback_llm_provider

        if assignment == "fast":
            # Fast tasks go directly to Groq fast model
            return ("groq", settings.groq_fast_model)
        else:
            if primary == "ibm":
                return ("ibm", settings.ibm_granite_model)
            else:
                return ("groq", settings.groq_primary_model)

    async def complete(
        self,
        task: str,
        system_prompt: str,
        user_message: str,
        response_format: Optional[dict] = None,
    ) -> dict:
        """
        Main entry point for all AI requests.
        Returns: {"content": str, "provider": str, "model": str, "fallback_used": bool}
        """
        provider_name, model = self._resolve_provider(task)
        start = time.time()

        # Attempt primary
        try:
            result = await self._call_provider(
                provider_name, model, system_prompt, user_message, response_format
            )
            latency = (time.time() - start) * 1000
            self._log_request(provider_name, model, task, True, latency, False)
            return {**result, "provider": provider_name, "model": model, "fallback_used": False}

        except Exception as e:
            logger.warning(f"Primary provider {provider_name} failed for task={task}: {e}")
            latency = (time.time() - start) * 1000
            self._log_request(provider_name, model, task, False, latency, False, str(type(e).__name__))

        # Attempt fallback
        fallback_name = settings.fallback_llm_provider
        fallback_model = settings.groq_primary_model
        start2 = time.time()

        try:
            result = await self._call_provider(
                fallback_name, fallback_model, system_prompt, user_message, response_format
            )
            latency2 = (time.time() - start2) * 1000
            self._log_request(fallback_name, fallback_model, task, True, latency2, True)
            logger.info(f"Fallback succeeded: {fallback_name}/{fallback_model}")
            return {**result, "provider": fallback_name, "model": fallback_model, "fallback_used": True}

        except Exception as e2:
            latency2 = (time.time() - start2) * 1000
            self._log_request(fallback_name, fallback_model, task, False, latency2, True, str(type(e2).__name__))
            logger.error(f"All providers failed for task={task}: {e2}")

        # Safe deterministic fallback
        return {
            "content": None,
            "provider": "deterministic_fallback",
            "model": "none",
            "fallback_used": True,
            "error": "All AI providers unavailable",
        }

    async def _call_provider(
        self,
        provider: str,
        model: str,
        system_prompt: str,
        user_message: str,
        response_format: Optional[dict],
    ) -> dict:
        if provider == "ibm":
            p = self._get_ibm_provider()
        else:
            p = self._get_groq_provider()
        return await p.complete(system_prompt, user_message, model, response_format)

    def _log_request(
        self,
        provider: str,
        model: str,
        task: str,
        success: bool,
        latency_ms: float,
        fallback_used: bool,
        error_type: Optional[str] = None,
    ):
        if self.db:
            try:
                record = AIRequest(
                    provider=provider,
                    model=model,
                    task=task,
                    success=success,
                    latency_ms=latency_ms,
                    fallback_used=fallback_used,
                    error_type=error_type,
                )
                self.db.add(record)
                self.db.commit()
            except Exception:
                pass  # Never crash request on logging failure
