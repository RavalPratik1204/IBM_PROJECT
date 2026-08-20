"""Segregation API — guidance, compliance, stats."""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User

router = APIRouter()


class ComplianceRecord(BaseModel):
    ward_id: Optional[int] = None
    is_compliant: bool
    waste_category: Optional[str] = None
    notes: Optional[str] = None


@router.post("/compliance")
def record_compliance(
    req: ComplianceRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.segregation_agent import SegregationAgent
    agent = SegregationAgent(db)
    record = agent.record_compliance(
        citizen_id=None,
        ward_id=req.ward_id,
        is_compliant=req.is_compliant,
        waste_category=req.waste_category,
        notes=req.notes,
    )
    return {"id": record.id, "recorded_at": record.recorded_at.isoformat()}


@router.get("/compliance/ward/{ward_id}")
def ward_compliance(
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.segregation_agent import SegregationAgent
    return SegregationAgent(db).get_ward_compliance_stats(ward_id)


@router.get("/compliance/all")
def all_wards_compliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.segregation_agent import SegregationAgent
    return SegregationAgent(db).get_all_wards_compliance()
