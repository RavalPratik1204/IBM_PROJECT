"""
Municipal Routing Agent — Agent 2.

Goal: Given a classified complaint, determine the correct department,
      ward assignment, team, priority, and required action.

Uses deterministic rules first, then LLM for reasoning enhancement.
"""
import json
import re
from typing import Optional
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.ai.router.provider_router import AIProviderRouter
from app.ai.prompts.system_prompts import ROUTING_SYSTEM_PROMPT
from app.models.user import Complaint, Department

logger = get_logger(__name__)

# Deterministic category → department mapping
# LLM is used to enhance reasoning, not replace this table
CATEGORY_DEPT_MAP = {
    "waste_collection":  "WASTE_COLLECTION",
    "overflow_bin":      "WASTE_COLLECTION",
    "illegal_dumping":   "SANITATION",
    "roadside_garbage":  "SANITATION",
    "segregation_issue": "SEGREGATION",
    "recycling_issue":   "RECYCLING",
    "schedule_issue":    "WASTE_COLLECTION",
    "other":             "GENERAL",
}

PRIORITY_ESCALATION = {
    "critical": True,
    "high": True,
    "medium": False,
    "low": False,
}


def _deterministic_route(complaint: Complaint) -> dict:
    """Fast, reliable routing based on category rules."""
    dept_code = CATEGORY_DEPT_MAP.get(complaint.category or "other", "GENERAL")
    priority = complaint.priority.value if complaint.priority else "medium"
    return {
        "department_code": dept_code,
        "team": f"Ward {complaint.ward_id or 'General'} Collection Team",
        "priority": priority,
        "action_required": f"Handle {(complaint.category or 'waste').replace('_', ' ')} complaint",
        "routing_reason": f"Automatically routed based on category: {complaint.category}",
        "escalate": PRIORITY_ESCALATION.get(priority, False),
    }


class MunicipalRoutingAgent:
    NAME = "ROUTING_AGENT"

    def __init__(self, db: Session):
        self.db = db
        self.router = AIProviderRouter(db)

    async def process(self, complaint: Complaint) -> Optional[dict]:
        """
        Route a classified complaint to the correct department.
        1. Deterministic rule gives baseline routing
        2. LLM enhances the routing reason and action description
        3. Falls back to deterministic if LLM fails
        """
        # Step 1: deterministic baseline (always reliable)
        base = _deterministic_route(complaint)

        # Step 2: LLM enhancement for reasoning
        user_message = (
            f"Complaint category: {complaint.category}\n"
            f"Description: {complaint.description or complaint.original_text[:200]}\n"
            f"Priority: {complaint.priority}\n"
            f"Ward: {complaint.ward_id}\n"
            f"Deterministic department: {base['department_code']}\n"
            f"Please confirm or refine the routing and provide a clear routing_reason."
        )

        result = await self.router.complete(
            task="routing_reasoning",
            system_prompt=ROUTING_SYSTEM_PROMPT,
            user_message=user_message,
            response_format={"type": "json_object"},
        )

        content = result.get("content")
        if content:
            # Extract JSON
            content = re.sub(r"```json\s*|```\s*", "", content).strip()
            try:
                parsed = json.loads(content)
                # Always trust deterministic dept over LLM (safety rule)
                parsed["department_code"] = base["department_code"]
                parsed["_provider"] = result.get("provider")
                return parsed
            except Exception:
                logger.warning(f"[{self.NAME}] LLM routing parse failed, using deterministic")

        base["_provider"] = "deterministic_fallback"
        return base
