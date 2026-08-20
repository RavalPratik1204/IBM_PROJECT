"""
Waste Segregation Agent — Agent 3.

Goal: Guide citizens on waste segregation, answer waste-category questions,
      track compliance, and generate ward-level segregation statistics.

Input:  Citizen question about waste categorization
Output: Guidance text + category classification
"""
import json
import re
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.logging import get_logger
from app.ai.router.provider_router import AIProviderRouter
from app.ai.prompts.system_prompts import SEGREGATION_SYSTEM_PROMPT
from app.models.user import SegregationRecord, WasteCategory

logger = get_logger(__name__)

# Static knowledge base — deterministic fallback
# Labeled as general guidelines, not local regulations
SEGREGATION_GUIDE = {
    "wet": {
        "bin_color": "Green",
        "examples": ["food scraps", "vegetable peels", "cooked food", "garden waste", "tea bags"],
        "label": "General Guideline — verify with local municipality"
    },
    "dry": {
        "bin_color": "Blue",
        "examples": ["paper", "cardboard", "plastic bottles", "glass", "metal cans", "newspapers"],
        "label": "General Guideline — verify with local municipality"
    },
    "hazardous": {
        "bin_color": "Red",
        "examples": ["batteries", "medicines", "paint", "chemicals", "motor oil", "fluorescent bulbs", "e-waste"],
        "label": "General Guideline — verify with local municipality"
    },
    "recyclable": {
        "bin_color": "Blue (clean items only)",
        "examples": ["clean plastic", "glass bottles", "tin cans", "newspapers", "cardboard"],
        "label": "General Guideline — verify with local municipality"
    },
    "non_recyclable": {
        "bin_color": "Black/Grey",
        "examples": ["soiled plastic", "thermocol", "sanitary waste", "diapers", "cigarette butts"],
        "label": "General Guideline — verify with local municipality"
    },
}

HAZARDOUS_KEYWORDS = ["battery", "batteries", "medicine", "chemical", "paint", "electronic", 
                      "e-waste", "mobile", "phone", "bulb", "बैटरी", "દવા", "કેમિકલ"]


def _quick_category(question: str) -> Optional[str]:
    """Fast keyword-based category detection."""
    q = question.lower()
    if any(kw in q for kw in HAZARDOUS_KEYWORDS):
        return "hazardous"
    if any(kw in q for kw in ["food", "vegetable", "fruit", "cooked", "खाना", "ભોજન", "શાક"]):
        return "wet"
    if any(kw in q for kw in ["paper", "bottle", "plastic", "glass", "card", "newspaper"]):
        return "dry"
    return None


class SegregationAgent:
    NAME = "SEGREGATION_AGENT"

    def __init__(self, db: Session):
        self.db = db
        self.router = AIProviderRouter(db)

    async def answer_question(self, question: str, language: str = "en") -> dict:
        """
        Answer a citizen's waste segregation question.
        Returns guidance text and detected waste category.
        """
        # Fast path: keyword detection
        quick_cat = _quick_category(question)

        result = await self.router.complete(
            task="segregation_guidance",
            system_prompt=SEGREGATION_SYSTEM_PROMPT,
            user_message=question,
        )

        content = result.get("content")
        if not content:
            # Deterministic fallback
            if quick_cat and quick_cat in SEGREGATION_GUIDE:
                guide = SEGREGATION_GUIDE[quick_cat]
                content = (
                    f"This is {quick_cat} waste. Use the {guide['bin_color']} bin.\n"
                    f"Examples: {', '.join(guide['examples'][:4])}\n"
                    f"⚠️ {guide['label']}"
                )
            else:
                content = "Please separate wet waste (food) from dry waste (paper/plastic). For hazardous items like batteries, contact your ward office. ⚠️ General Guideline — verify with local municipality."

        return {
            "guidance": content,
            "detected_category": quick_cat,
            "provider": result.get("provider", "deterministic_fallback"),
            "disclaimer": "General Guidelines — Not Official Municipal Policy",
        }

    def record_compliance(
        self,
        citizen_id: Optional[int],
        ward_id: Optional[int],
        is_compliant: bool,
        waste_category: Optional[str] = None,
        notes: Optional[str] = None,
        is_demo: bool = False,
    ) -> SegregationRecord:
        """Record a segregation compliance observation."""
        cat = None
        if waste_category:
            try:
                cat = WasteCategory(waste_category)
            except ValueError:
                pass

        record = SegregationRecord(
            citizen_id=citizen_id,
            ward_id=ward_id,
            is_compliant=is_compliant,
            waste_category=cat,
            notes=notes,
            is_demo_data=is_demo,
        )
        self.db.add(record)
        self.db.commit()
        return record

    def get_ward_compliance_stats(self, ward_id: int) -> dict:
        """Returns compliance statistics for a ward."""
        total = self.db.query(SegregationRecord).filter(
            SegregationRecord.ward_id == ward_id
        ).count()

        compliant = self.db.query(SegregationRecord).filter(
            SegregationRecord.ward_id == ward_id,
            SegregationRecord.is_compliant == True,
        ).count()

        rate = round((compliant / total * 100), 1) if total > 0 else 0.0

        return {
            "ward_id": ward_id,
            "total_records": total,
            "compliant": compliant,
            "non_compliant": total - compliant,
            "compliance_rate_pct": rate,
        }

    def get_all_wards_compliance(self) -> list:
        """Returns compliance stats for all wards."""
        from app.models.user import Ward
        wards = self.db.query(Ward).filter(Ward.is_active == True).all()
        return [self.get_ward_compliance_stats(w.id) for w in wards]
