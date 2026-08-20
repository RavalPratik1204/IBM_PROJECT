"""Analytics API — KPIs, trends, ward performance, AI stats."""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User

router = APIRouter()


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.analytics_agent import WardAnalyticsAgent
    agent = WardAnalyticsAgent(db)
    return agent.get_overview_kpis()


@router.get("/by-ward")
def by_ward(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.analytics_agent import WardAnalyticsAgent
    return WardAnalyticsAgent(db).get_complaints_by_ward()


@router.get("/by-category")
def by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.analytics_agent import WardAnalyticsAgent
    return WardAnalyticsAgent(db).get_complaints_by_category()


@router.get("/daily-trend")
def daily_trend(
    days: int = 14,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.analytics_agent import WardAnalyticsAgent
    return WardAnalyticsAgent(db).get_daily_trend(days)


@router.get("/ward-performance")
def ward_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.analytics_agent import WardAnalyticsAgent
    return WardAnalyticsAgent(db).get_ward_performance()


@router.get("/ai-providers")
def ai_provider_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.analytics_agent import WardAnalyticsAgent
    return WardAnalyticsAgent(db).get_ai_provider_stats()


@router.get("/summary")
async def ai_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.analytics_agent import WardAnalyticsAgent
    agent = WardAnalyticsAgent(db)
    summary = await agent.generate_summary()
    return {"summary": summary}
