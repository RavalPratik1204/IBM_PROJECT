"""
Groq Provider — wraps the Groq Python SDK.
API key is read from env, never hard-coded.
"""
import json
from typing import Optional
from groq import AsyncGroq
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroqProvider:
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not configured in .env")
        self.client = AsyncGroq(api_key=settings.groq_api_key)

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        model: Optional[str] = None,
        response_format: Optional[dict] = None,
    ) -> dict:
        model = model or settings.groq_primary_model

        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.1,
            "max_tokens": 1024,
        }

        # Request JSON output when schema provided
        if response_format:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        logger.debug(f"Groq [{model}] responded ({len(content)} chars)")
        return {"content": content}
