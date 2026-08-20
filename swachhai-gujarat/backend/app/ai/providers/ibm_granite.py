"""
IBM Granite Provider — wraps ibm-watsonx-ai SDK.
Credentials read from env. Gracefully skips when not configured.
"""
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class IBMGraniteProvider:
    def __init__(self):
        if not settings.ibm_api_key or not settings.ibm_project_id:
            raise ValueError(
                "IBM_API_KEY and IBM_PROJECT_ID must be configured in .env for IBM Granite"
            )
        # Lazy import — only fails if credentials are missing
        try:
            from ibm_watsonx_ai import APIClient, Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference

            credentials = Credentials(
                url=settings.ibm_watsonx_url,
                api_key=settings.ibm_api_key,
            )
            self.model = ModelInference(
                model_id=settings.ibm_granite_model,
                credentials=credentials,
                project_id=settings.ibm_project_id,
            )
        except ImportError:
            raise ImportError("ibm-watsonx-ai package not installed. Run: pip install ibm-watsonx-ai")

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        model: Optional[str] = None,
        response_format: Optional[dict] = None,
    ) -> dict:
        """
        IBM watsonx.ai text generation. 
        Converts chat-style prompt to instruction format for Granite.
        """
        prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_message}\n<|assistant|>\n"

        params = {
            "max_new_tokens": 1024,
            "temperature": 0.1,
            "stop_sequences": ["<|user|>", "<|system|>"],
        }

        # ibm_watsonx_ai is synchronous — run in executor for async compatibility
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.model.generate_text(prompt=prompt, params=params)
        )

        logger.debug(f"IBM Granite responded ({len(result)} chars)")
        return {"content": result}
