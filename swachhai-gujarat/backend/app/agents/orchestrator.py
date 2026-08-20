"""
Agent Orchestrator — coordinates all agents for a complaint lifecycle.
This is what makes the system truly agentic: agents are triggered in sequence,
each consuming the output of the previous, with logging at every step.
"""
import json
import re
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.user import Complaint, AgentLog, ComplaintStatus, ComplaintPriority

logger = get_logger(__name__)


def _log(db: Session, complaint_id: Optional[int], agent: str, event: str, detail: str = None, provider: str = None, latency: float = None):
    """Write an agent log entry visible in the dashboard."""
    entry = AgentLog(
        complaint_id=complaint_id,
        agent_name=agent,
        event=event,
        detail=detail,
        ai_provider=provider,
        latency_ms=latency,
    )
    db.add(entry)
    db.commit()
    logger.info(f"[{agent}] {event}")


async def run_complaint_pipeline(
    complaint: Complaint,
    db: Session,
) -> Complaint:
    """
    Full agentic pipeline for a new complaint:
    1. Grievance Intake Agent — classify and extract
    2. Municipal Routing Agent — assign department/ward/priority
    3. Route Optimization Agent — if collection-related
    Returns the updated complaint.
    """
    complaint_id = complaint.id
    _log(db, complaint_id, "ORCHESTRATOR", "Pipeline started", f"ticket={complaint.ticket_id}")

    # ── Agent 1: Grievance Intake ─────────────────────────────────────────
    from app.agents.grievance_agent import GrievanceIntakeAgent
    grievance_agent = GrievanceIntakeAgent(db)
    t0 = datetime.utcnow()
    structured = await grievance_agent.process(complaint)
    latency = (datetime.utcnow() - t0).total_seconds() * 1000

    if structured:
        complaint.category = structured.get("category")
        complaint.language = structured.get("language", complaint.language)
        complaint.description = structured.get("description")
        complaint.ai_confidence = structured.get("confidence")
        complaint.requires_route_optimization = structured.get("requires_route_optimization", False)
        raw_priority = structured.get("priority", "medium")
        try:
            complaint.priority = ComplaintPriority(raw_priority)
        except ValueError:
            complaint.priority = ComplaintPriority.medium

        db.commit()
        _log(db, complaint_id, "GRIEVANCE_AGENT", "Complaint classified",
             f"category={complaint.category} | priority={complaint.priority} | lang={complaint.language}",
             structured.get("_provider"), latency)
    else:
        _log(db, complaint_id, "GRIEVANCE_AGENT", "Classification failed — using defaults")

    # ── Agent 2: Municipal Routing ────────────────────────────────────────
    from app.agents.routing_agent import MunicipalRoutingAgent
    routing_agent = MunicipalRoutingAgent(db)
    t1 = datetime.utcnow()
    routing = await routing_agent.process(complaint)
    latency2 = (datetime.utcnow() - t1).total_seconds() * 1000

    if routing:
        dept = routing.get("department_code")
        from app.models.user import Department
        department = db.query(Department).filter(Department.code == dept).first()
        if department:
            complaint.department_id = department.id

        complaint.routing_reason = routing.get("routing_reason")
        # Override priority if routing agent escalates
        if routing.get("escalate") and complaint.priority not in [ComplaintPriority.critical]:
            complaint.priority = ComplaintPriority.high

        complaint.status = ComplaintStatus.assigned
        db.commit()
        _log(db, complaint_id, "ROUTING_AGENT", "Complaint routed",
             f"dept={dept} | action={routing.get('action_required')}",
             routing.get("_provider"), latency2)
    else:
        _log(db, complaint_id, "ROUTING_AGENT", "Routing failed — complaint stays unassigned")

    # ── Agent 3: Route Optimization (conditional) ─────────────────────────
    if complaint.requires_route_optimization and complaint.ward_id:
        from app.agents.route_optimization_agent import RouteOptimizationAgent
        route_agent = RouteOptimizationAgent(db)
        t2 = datetime.utcnow()
        route_result = await route_agent.optimize_for_ward(complaint.ward_id)
        latency3 = (datetime.utcnow() - t2).total_seconds() * 1000
        _log(db, complaint_id, "ROUTE_AGENT",
             "Route optimization triggered",
             f"ward_id={complaint.ward_id} | stops={route_result.get('stop_count', 0)}",
             None, latency3)

    _log(db, complaint_id, "ORCHESTRATOR", "Pipeline complete", f"status={complaint.status}")
    return complaint
