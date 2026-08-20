"""Routes API — collection routes, bins, vehicles."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import CollectionRoute, WasteBin, Vehicle, User

router = APIRouter()


@router.get("/active")
def active_routes(
    ward_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    from app.agents.route_optimization_agent import RouteOptimizationAgent
    agent = RouteOptimizationAgent(db)
    routes = agent.get_active_routes(ward_id)
    return [
        {
            "id": r.id,
            "route_code": r.route_code,
            "ward_id": r.ward_id,
            "vehicle_id": r.vehicle_id,
            "status": r.status,
            "total_distance_km": r.total_distance_km,
            "estimated_duration_min": r.estimated_duration_min,
            "stop_count": len(r.stops),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in routes
    ]


@router.get("/{route_id}/stops")
def route_stops(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    route = db.query(CollectionRoute).filter(CollectionRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return [
        {
            "stop_order": s.stop_order,
            "bin_id": s.bin_id,
            "bin_code": s.bin.bin_code if s.bin else None,
            "latitude": s.bin.latitude if s.bin else None,
            "longitude": s.bin.longitude if s.bin else None,
            "fill_level_pct": s.bin.fill_level_pct if s.bin else None,
            "is_overflow": s.bin.is_overflow if s.bin else None,
            "distance_from_prev_km": s.distance_from_prev_km,
            "is_completed": s.is_completed,
        }
        for s in route.stops
    ]


@router.get("/bins")
def list_bins(
    ward_id: Optional[int] = None,
    overflow_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    q = db.query(WasteBin).filter(WasteBin.is_active == True)
    if ward_id:
        q = q.filter(WasteBin.ward_id == ward_id)
    if overflow_only:
        q = q.filter(WasteBin.is_overflow == True)
    bins = q.all()
    return [
        {
            "id": b.id,
            "bin_code": b.bin_code,
            "ward_id": b.ward_id,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "fill_level_pct": b.fill_level_pct,
            "is_overflow": b.is_overflow,
            "capacity_liters": b.capacity_liters,
            "waste_category": b.waste_category.value if b.waste_category else None,
            "last_collected": b.last_collected.isoformat() if b.last_collected else None,
            "is_demo_data": b.is_demo_data,
        }
        for b in bins
    ]
