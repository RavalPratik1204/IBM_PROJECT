"""
Route Optimization Agent — Agent 4.

Goal: Given waste bins in a ward, calculate an optimized collection route
      that minimizes distance while prioritizing high-fill and overflow bins.

Algorithm: Priority-weighted nearest-neighbor (greedy TSP approximation).
The LLM is NOT used for route calculation — math is deterministic and reliable.
"""
import math
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.user import WasteBin, CollectionRoute, RouteStop, Vehicle

logger = get_logger(__name__)


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _priority_score(bin: WasteBin) -> float:
    """
    Higher score = higher priority for collection.
    Overflow bins always go first. Fill level 70%+ is urgent.
    """
    score = bin.fill_level_pct or 0.0
    if bin.is_overflow:
        score += 50.0
    return score


def _nearest_neighbor_route(
    bins: List[WasteBin],
    start_lat: float = None,
    start_lon: float = None,
) -> List[WasteBin]:
    """
    Priority-weighted nearest-neighbor route optimization.
    1. Sort bins: overflow first, then by fill level descending.
    2. From current position, always visit nearest unvisited high-priority bin.
    """
    if not bins:
        return []

    # Separate critical bins (overflow + >80% fill)
    critical = [b for b in bins if b.is_overflow or (b.fill_level_pct or 0) >= 80]
    normal = [b for b in bins if b not in critical]

    # Sort critical by priority score
    critical.sort(key=_priority_score, reverse=True)

    # For normal bins, apply nearest-neighbor
    if start_lat is None and bins:
        start_lat = bins[0].latitude
        start_lon = bins[0].longitude

    ordered = list(critical)
    remaining = list(normal)
    cur_lat, cur_lon = start_lat, start_lon

    while remaining:
        nearest = min(remaining, key=lambda b: _haversine(cur_lat, cur_lon, b.latitude, b.longitude))
        ordered.append(nearest)
        remaining.remove(nearest)
        cur_lat, cur_lon = nearest.latitude, nearest.longitude

    return ordered


def _calculate_total_distance(route: List[WasteBin]) -> float:
    """Sum of all inter-stop distances in km."""
    total = 0.0
    for i in range(1, len(route)):
        total += _haversine(
            route[i-1].latitude, route[i-1].longitude,
            route[i].latitude, route[i].longitude,
        )
    return round(total, 2)


class RouteOptimizationAgent:
    NAME = "ROUTE_AGENT"
    AVG_SPEED_KMH = 20.0  # conservative urban speed

    def __init__(self, db: Session):
        self.db = db

    async def optimize_for_ward(
        self,
        ward_id: int,
        vehicle_id: Optional[int] = None,
        min_fill_pct: float = 40.0,
    ) -> dict:
        """
        Calculate optimized collection route for a ward.
        Only includes bins at or above min_fill_pct threshold.
        Returns route summary dict.
        """
        logger.info(f"[{self.NAME}] Optimizing route for ward_id={ward_id}")

        # Fetch bins that need collection
        bins = (
            self.db.query(WasteBin)
            .filter(
                WasteBin.ward_id == ward_id,
                WasteBin.is_active == True,
                WasteBin.fill_level_pct >= min_fill_pct,
            )
            .all()
        )

        if not bins:
            logger.info(f"[{self.NAME}] No bins need collection in ward {ward_id}")
            return {"ward_id": ward_id, "stop_count": 0, "message": "No bins require collection"}

        # Calculate optimized order
        ordered_bins = _nearest_neighbor_route(bins)
        total_km = _calculate_total_distance(ordered_bins)
        estimated_min = round((total_km / self.AVG_SPEED_KMH) * 60 + len(ordered_bins) * 3, 1)

        # Get or assign vehicle
        if not vehicle_id:
            vehicle = (
                self.db.query(Vehicle)
                .filter(Vehicle.ward_id == ward_id, Vehicle.is_available == True)
                .first()
            )
            vehicle_id = vehicle.id if vehicle else None

        # Persist route
        route_code = f"RT-{ward_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        route = CollectionRoute(
            route_code=route_code,
            vehicle_id=vehicle_id,
            ward_id=ward_id,
            status="planned",
            total_distance_km=total_km,
            estimated_duration_min=estimated_min,
            optimization_algorithm="priority_nearest_neighbor",
        )
        self.db.add(route)
        self.db.flush()

        prev_lat = ordered_bins[0].latitude if ordered_bins else 0
        prev_lon = ordered_bins[0].longitude if ordered_bins else 0

        for idx, bin_obj in enumerate(ordered_bins):
            dist = 0.0 if idx == 0 else _haversine(prev_lat, prev_lon, bin_obj.latitude, bin_obj.longitude)
            stop = RouteStop(
                route_id=route.id,
                bin_id=bin_obj.id,
                stop_order=idx + 1,
                distance_from_prev_km=round(dist, 3),
            )
            self.db.add(stop)
            prev_lat, prev_lon = bin_obj.latitude, bin_obj.longitude

        self.db.commit()

        logger.info(f"[{self.NAME}] Route {route_code}: {len(ordered_bins)} stops, {total_km} km, ~{estimated_min} min")

        return {
            "route_id": route.id,
            "route_code": route_code,
            "ward_id": ward_id,
            "stop_count": len(ordered_bins),
            "total_distance_km": total_km,
            "estimated_duration_min": estimated_min,
            "vehicle_id": vehicle_id,
            "priority_bins": sum(1 for b in ordered_bins if b.is_overflow or (b.fill_level_pct or 0) >= 80),
            "algorithm": "priority_nearest_neighbor",
        }

    def get_active_routes(self, ward_id: Optional[int] = None) -> list:
        """Return routes for dashboard display."""
        q = self.db.query(CollectionRoute).filter(CollectionRoute.status.in_(["planned", "active"]))
        if ward_id:
            q = q.filter(CollectionRoute.ward_id == ward_id)
        return q.order_by(CollectionRoute.created_at.desc()).limit(20).all()
