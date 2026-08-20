"""
Grievance Intake Agent — Agent 1.

Goal: Understand a citizen complaint in any supported language,
      extract structured information, and return a validated JSON object.

Input:  Complaint ORM object (original_text, language hint)
Output: dict with category, priority, language, description, confidence
"""
import json
import re
from typing import Optional
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.ai.router.provider_router import AIProviderRouter
from app.ai.prompts.system_prompts import GRIEVANCE_INTAKE_SYSTEM_PROMPT
from app.models.user import Complaint

logger = get_logger(__name__)

# Deterministic fallback — keyword-based classification when AI unavailable
# Order matters: more specific categories before generic ones.
# roadside_garbage must precede waste_collection so "road side garbage" routes correctly.
KEYWORD_MAP = {
    "overflow_bin":      ["overflow", "full bin", "overflowing", "ઉભરાઈ", "उभरा"],
    "illegal_dumping":   ["illegal", "dump", "dumping", "ગેરકાયદે", "अवैध"],
    "roadside_garbage":  ["roadside", "road side", "on the road", "rasta", "street garbage", "રોડ", "सड़क"],
    "segregation_issue": ["segregat", "mix", "separate", "અલગ", "अलग"],
    "waste_collection":  [
        "garbage", "trash", "collect", "pickup",
        "kachro", "kachara", "kachra",
        "कचरा", "कचरो", "उठाया", "उठाव",
        "ઉઠ", "ઉઠાવ", "ઉઠ્ય", "ઉઠ", "ઉઠાવ",
        "ઉઠ\u0abe\u0ab5", "ઉ\u0aaa\u0abe\u0aa1",   # ઉઠ + various vowel combos
    ],
}


def _keyword_classify(text: str) -> str:
    # For non-ASCII (Gujarati/Hindi), search the raw Unicode text directly
    for category, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in text or kw in text.lower():
                return category
    return "other"


def _detect_language(text: str) -> str:
    # Simple Unicode-range based detection
    gujarati_chars = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF')
    devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    if gujarati_chars > 2:
        return "gu"
    if devanagari_chars > 2:
        return "hi"
    return "en"


def _parse_json_response(content: str) -> Optional[dict]:
    """Safely parse JSON from AI response, handling markdown fences."""
    if not content:
        return None
    # Strip markdown code fences if present
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content)
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON object from response
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def _validate_structured_output(data: dict) -> bool:
    """Validate required fields before database insertion."""
    required = ["category", "language", "priority", "description"]
    valid_categories = ["waste_collection", "overflow_bin", "illegal_dumping",
                       "roadside_garbage", "segregation_issue", "recycling_issue",
                       "schedule_issue", "other"]
    valid_priorities = ["low", "medium", "high", "critical"]

    for field in required:
        if field not in data:
            return False
    if data.get("category") not in valid_categories:
        return False
    if data.get("priority") not in valid_priorities:
        return False
    return True


class GrievanceIntakeAgent:
    NAME = "GRIEVANCE_AGENT"

    def __init__(self, db: Session):
        self.db = db
        self.router = AIProviderRouter(db)

    async def process(self, complaint: Complaint) -> Optional[dict]:
        """
        Process a complaint through the Grievance Intake Agent.
        Returns structured data dict or None if all methods fail.
        """
        text = complaint.original_text

        # Pre-detect language (deterministic, fast)
        detected_lang = _detect_language(text)
        logger.info(f"[{self.NAME}] Language detected: {detected_lang}")

        # Build user message for AI
        user_message = f"Citizen complaint: {text}"

        # Call AI via router
        result = await self.router.complete(
            task="complaint_classification",
            system_prompt=GRIEVANCE_INTAKE_SYSTEM_PROMPT,
            user_message=user_message,
            response_format={"type": "json_object"},
        )

        content = result.get("content")
        provider = result.get("provider")

        if content:
            parsed = _parse_json_response(content)
            if parsed and _validate_structured_output(parsed):
                parsed["_provider"] = provider
                # Override language detection with AI result if confident
                if detected_lang != "en":
                    parsed["language"] = detected_lang
                return parsed
            else:
                logger.warning(f"[{self.NAME}] AI output invalid, using deterministic fallback")

        # Deterministic fallback
        logger.warning(f"[{self.NAME}] Using keyword-based fallback classification")
        return {
            "category": _keyword_classify(text),
            "language": detected_lang,
            "priority": "medium",
            "description": text[:200],  # truncated original
            "requires_route_optimization": True,
            "ward": None,
            "location": None,
            "confidence": 0.4,
            "_provider": "deterministic_fallback",
        }

    async def handle_chat(self, message: str, history: list) -> str:
        """
        Conversational interface — citizen chat assistant.
        Returns a natural language response.
        """
        history_text = "\n".join([f"{h['role']}: {h['content']}" for h in history[-5:]])
        user_msg = f"Previous conversation:\n{history_text}\n\nCitizen: {message}"

        result = await self.router.complete(
            task="chat_response",
            system_prompt=GRIEVANCE_INTAKE_SYSTEM_PROMPT,
            user_message=user_msg,
        )
        return result.get("content") or "I'm sorry, I couldn't process your request. Please try again or call the municipal helpline."
