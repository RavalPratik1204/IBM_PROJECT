"""
Complaints API — submit, list, update, track.
Triggers the full agentic pipeline on creation.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import (
    Complaint, ComplaintStatus, ComplaintPriority,
    Ward, User, AgentLog
)
from app.agents.orchestrator import run_complaint_pipeline

router = APIRouter()


class ComplaintCreateRequest(BaseModel):
    original_text: str
    language: str = "en"
    ward_id: Optional[int] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_source: str = "user_entered"


class ComplaintUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None
    department_id: Optional[int] = None


def _generate_ticket_id() -> str:
    return f"SG-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"


def _complaint_to_dict(c: Complaint) -> dict:
    return {
        "id": c.id,
        "ticket_id": c.ticket_id,
        "original_text": c.original_text,
        "language": c.language,
        "description": c.description,
        "category": c.category,
        "priority": c.priority.value if c.priority else None,
        "status": c.status.value if c.status else None,
        "ward_id": c.ward_id,
        "address": c.address,
        "latitude": c.latitude,
        "longitude": c.longitude,
        "department_id": c.department_id,
        "routing_reason": c.routing_reason,
        "ai_confidence": c.ai_confidence,
        "ai_provider": c.ai_provider,
        "requires_route_optimization": c.requires_route_optimization,
        "is_demo_data": c.is_demo_data,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
    }


@router.post("")
async def submit_complaint(
    req: ComplaintCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    complaint = Complaint(
        ticket_id=_generate_ticket_id(),
        citizen_id=current_user.id if current_user else None,
        citizen_name=current_user.name if current_user else "Anonymous",
        original_text=req.original_text,
        language=req.language,
        ward_id=req.ward_id,
        address=req.address,
        latitude=req.latitude,
        longitude=req.longitude,
        location_source=req.location_source,
        status=ComplaintStatus.new,
        priority=ComplaintPriority.medium,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Run agentic pipeline asynchronously
    background_tasks.add_task(run_complaint_pipeline, complaint, db)

    return {"ticket_id": complaint.ticket_id, "id": complaint.id, "status": "processing"}


@router.get("")
def list_complaints(
    ward_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    q = db.query(Complaint)
    if ward_id:
        q = q.filter(Complaint.ward_id == ward_id)
    if status:
        q = q.filter(Complaint.status == status)
    if category:
        q = q.filter(Complaint.category == category)
    if priority:
        q = q.filter(Complaint.priority == priority)
    total = q.count()
    complaints = q.order_by(Complaint.created_at.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": [_complaint_to_dict(c) for c in complaints]}


@router.get("/my")
def my_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaints = (
        db.query(Complaint)
        .filter(Complaint.citizen_id == current_user.id)
        .order_by(Complaint.created_at.desc())
        .limit(20)
        .all()
    )
    return [_complaint_to_dict(c) for c in complaints]


@router.get("/{ticket_id}")
def get_complaint(ticket_id: str, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter(Complaint.ticket_id == ticket_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")
    data = _complaint_to_dict(c)
    # Include agent logs for tracking
    logs = db.query(AgentLog).filter(AgentLog.complaint_id == c.id).order_by(AgentLog.created_at).all()
    data["agent_logs"] = [
        {
            "agent": log.agent_name,
            "event": log.event,
            "detail": log.detail,
            "provider": log.ai_provider,
            "timestamp": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
    return data


@router.patch("/{complaint_id}")
def update_complaint(
    complaint_id: int,
    req: ComplaintUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    c = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if req.status:
        try:
            c.status = ComplaintStatus(req.status)
            if req.status == "resolved":
                c.resolved_at = datetime.utcnow()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {req.status}")
    if req.priority:
        try:
            c.priority = ComplaintPriority(req.priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {req.priority}")
    if req.assigned_to_id is not None:
        c.assigned_to_id = req.assigned_to_id
    if req.department_id is not None:
        c.department_id = req.department_id

    db.commit()
    return _complaint_to_dict(c)
