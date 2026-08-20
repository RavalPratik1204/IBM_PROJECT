"""
Agents API — direct agent interaction endpoints (chat, segregation Q&A, route trigger).
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import AgentLog, User

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    language: str = "en"
    history: List[dict] = []


class SegregationQuestion(BaseModel):
    question: str
    language: str = "en"


class RouteOptimizeRequest(BaseModel):
    ward_id: int
    min_fill_pct: float = 40.0


@router.post("/chat")
async def chat(req: ChatMessage, db: Session = Depends(get_db)):
    """Citizen chat interface — grievance intake and general assistance."""
    from app.agents.grievance_agent import GrievanceIntakeAgent
    agent = GrievanceIntakeAgent(db)
    response = await agent.handle_chat(req.message, req.history)
    return {"response": response}


@router.post("/segregation")
async def segregation_guidance(req: SegregationQuestion, db: Session = Depends(get_db)):
    """Waste segregation guidance for citizens."""
    from app.agents.segregation_agent import SegregationAgent
    agent = SegregationAgent(db)
    result = await agent.answer_question(req.question, req.language)
    return result


@router.post("/optimize-route")
async def optimize_route(
    req: RouteOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    """Manually trigger route optimization for a ward."""
    from app.agents.route_optimization_agent import RouteOptimizationAgent
    agent = RouteOptimizationAgent(db)
    result = await agent.optimize_for_ward(req.ward_id, min_fill_pct=req.min_fill_pct)
    return result


@router.get("/logs")
def get_agent_logs(
    complaint_id: Optional[int] = None,
    agent_name: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    """Agent activity log for the municipal dashboard."""
    q = db.query(AgentLog)
    if complaint_id:
        q = q.filter(AgentLog.complaint_id == complaint_id)
    if agent_name:
        q = q.filter(AgentLog.agent_name == agent_name)
    logs = q.order_by(AgentLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "complaint_id": log.complaint_id,
            "agent": log.agent_name,
            "event": log.event,
            "detail": log.detail,
            "provider": log.ai_provider,
            "latency_ms": log.latency_ms,
            "timestamp": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
