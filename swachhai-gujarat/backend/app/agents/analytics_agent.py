"""
Ward Analytics Agent — Agent 5.

Goal: Aggregate operational KPIs from the database,
      provide ward-level comparisons, trends, and AI-generated summaries.
      All numbers come from the database — never invented.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.logging import get_logger
from app.ai.router.provider_router import AIProviderRouter
from app.ai.prompts.system_prompts import ANALYTICS_SUMMARY_PROMPT
from app.models.user import (
    Complaint, ComplaintStatus, Ward, WasteBin,
    CollectionRoute, SegregationRecord, AIRequest
)

logger = get_logger(__name__)


class WardAnalyticsAgent:
    NAME = "ANALYTICS_AGENT"

    def __init__(self, db: Session):
        self.db = db
        self.router = AIProviderRouter(db)

    def get_overview_kpis(self) -> dict:
        """Top-level operational KPIs for the dashboard header."""
        total = self.db.query(Complaint).count()
        open_c = self.db.query(Complaint).filter(
            Complaint.status.in_([ComplaintStatus.new, ComplaintStatus.assigned, ComplaintStatus.in_progress])
        ).count()
        resolved = self.db.query(Complaint).filter(
            Complaint.status == ComplaintStatus.resolved
        ).count()
        overflow_bins = self.db.query(WasteBin).filter(WasteBin.is_overflow == True).count()

        # Average resolution time (in hours) for resolved complaints
        resolved_complaints = self.db.query(Complaint).filter(
            Complaint.status == ComplaintStatus.resolved,
            Complaint.resolved_at.isnot(None),
        ).all()
        avg_res_hrs = 0.0
        if resolved_complaints:
            durations = [
                (c.resolved_at - c.created_at).total_seconds() / 3600
                for c in resolved_complaints
                if c.resolved_at and c.created_at
            ]
            avg_res_hrs = round(sum(durations) / len(durations), 1) if durations else 0.0

        # Segregation compliance
        total_seg = self.db.query(SegregationRecord).count()
        compliant_seg = self.db.query(SegregationRecord).filter(
            SegregationRecord.is_compliant == True
        ).count()
        seg_rate = round((compliant_seg / total_seg * 100), 1) if total_seg > 0 else 0.0

        return {
            "total_complaints": total,
            "open_complaints": open_c,
            "resolved_complaints": resolved,
            "resolution_rate_pct": round((resolved / total * 100), 1) if total > 0 else 0.0,
            "avg_resolution_hours": avg_res_hrs,
            "overflow_bins": overflow_bins,
            "segregation_compliance_pct": seg_rate,
            "total_bins": self.db.query(WasteBin).count(),
        }

    def get_complaints_by_ward(self) -> list:
        """Complaint counts grouped by ward."""
        rows = (
            self.db.query(Ward.id, Ward.name, func.count(Complaint.id).label("count"))
            .outerjoin(Complaint, Complaint.ward_id == Ward.id)
            .group_by(Ward.id, Ward.name)
            .all()
        )
        return [{"ward_id": r.id, "ward_name": r.name, "complaint_count": r.count} for r in rows]

    def get_complaints_by_category(self) -> list:
        """Complaint counts grouped by category."""
        rows = (
            self.db.query(Complaint.category, func.count(Complaint.id).label("count"))
            .group_by(Complaint.category)
            .all()
        )
        return [{"category": r.category or "unknown", "count": r.count} for r in rows]

    def get_daily_trend(self, days: int = 14) -> list:
        """Daily complaint counts for the last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        rows = (
            self.db.query(
                func.date(Complaint.created_at).label("date"),
                func.count(Complaint.id).label("count"),
            )
            .filter(Complaint.created_at >= cutoff)
            .group_by(func.date(Complaint.created_at))
            .order_by(func.date(Complaint.created_at))
            .all()
        )
        return [{"date": str(r.date), "count": r.count} for r in rows]

    def get_ward_performance(self) -> list:
        """Per-ward KPIs: total, resolved, rate, avg_time."""
        wards = self.db.query(Ward).filter(Ward.is_active == True).all()
        result = []
        for ward in wards:
            total = self.db.query(Complaint).filter(Complaint.ward_id == ward.id).count()
            resolved = self.db.query(Complaint).filter(
                Complaint.ward_id == ward.id,
                Complaint.status == ComplaintStatus.resolved,
            ).count()
            overflow = self.db.query(WasteBin).filter(
                WasteBin.ward_id == ward.id,
                WasteBin.is_overflow == True,
            ).count()

            result.append({
                "ward_id": ward.id,
                "ward_name": ward.name,
                "total_complaints": total,
                "resolved_complaints": resolved,
                "resolution_rate_pct": round((resolved / total * 100), 1) if total > 0 else 0.0,
                "overflow_bins": overflow,
            })
        return result

    def get_ai_provider_stats(self) -> dict:
        """Actual measured AI provider performance — never invented."""
        providers = ["ibm", "groq", "deterministic_fallback"]
        stats = {}
        for provider in providers:
            total = self.db.query(AIRequest).filter(AIRequest.provider == provider).count()
            if total == 0:
                continue
            success = self.db.query(AIRequest).filter(
                AIRequest.provider == provider,
                AIRequest.success == True,
            ).count()
            avg_lat = self.db.query(func.avg(AIRequest.latency_ms)).filter(
                AIRequest.provider == provider
            ).scalar() or 0
            fallbacks = self.db.query(AIRequest).filter(
                AIRequest.provider == provider,
                AIRequest.fallback_used == True,
            ).count()
            stats[provider] = {
                "total_requests": total,
                "success_rate_pct": round((success / total * 100), 1),
                "avg_latency_ms": round(avg_lat, 1),
                "fallback_events": fallbacks,
            }
        return stats

    async def generate_summary(self) -> str:
        """AI-generated natural language summary of current operations."""
        kpis = self.get_overview_kpis()
        by_ward = self.get_complaints_by_ward()
        worst_ward = max(by_ward, key=lambda x: x["complaint_count"], default=None)
        by_cat = self.get_complaints_by_category()
        top_cat = max(by_cat, key=lambda x: x["count"], default=None)

        data_summary = (
            f"Total complaints: {kpis['total_complaints']}, "
            f"Open: {kpis['open_complaints']}, "
            f"Resolved: {kpis['resolved_complaints']}, "
            f"Resolution rate: {kpis['resolution_rate_pct']}%, "
            f"Overflow bins: {kpis['overflow_bins']}, "
            f"Segregation compliance: {kpis['segregation_compliance_pct']}%, "
            f"Top category: {top_cat['category'] if top_cat else 'N/A'} ({top_cat['count'] if top_cat else 0} cases), "
            f"Most complaints ward: {worst_ward['ward_name'] if worst_ward else 'N/A'}"
        )

        result = await self.router.complete(
            task="summarization",
            system_prompt=ANALYTICS_SUMMARY_PROMPT,
            user_message=data_summary,
        )
        return result.get("content") or f"Operations summary: {data_summary}"
