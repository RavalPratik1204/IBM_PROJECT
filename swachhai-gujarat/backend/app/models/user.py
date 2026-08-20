"""
SQLAlchemy ORM Models — all database tables.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# ── Enums ──────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    citizen = "citizen"
    officer = "officer"
    admin = "admin"


class ComplaintStatus(str, enum.Enum):
    new = "new"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class ComplaintPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class WasteCategory(str, enum.Enum):
    wet = "wet"
    dry = "dry"
    recyclable = "recyclable"
    non_recyclable = "non_recyclable"
    hazardous = "hazardous"


# ── User ───────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.citizen, nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    preferred_language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    complaints = relationship("Complaint", back_populates="citizen", foreign_keys="Complaint.citizen_id")
    ward = relationship("Ward", back_populates="users")


# ── Ward ───────────────────────────────────────────────────────────────────

class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    city = Column(String(100), default="Ahmedabad")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    population = Column(Integer, nullable=True)
    area_sqkm = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", back_populates="ward")
    complaints = relationship("Complaint", back_populates="ward")
    bins = relationship("WasteBin", back_populates="ward")


# ── Department ─────────────────────────────────────────────────────────────

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)

    complaints = relationship("Complaint", back_populates="department")


# ── Complaint ──────────────────────────────────────────────────────────────

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(20), unique=True, index=True, nullable=False)

    # Citizen info
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    citizen_name = Column(String(120), nullable=True)  # for anonymous

    # Content
    original_text = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    translated_text = Column(Text, nullable=True)
    description = Column(Text, nullable=True)  # structured English description

    # Classification
    category = Column(String(50), nullable=True)
    sub_category = Column(String(50), nullable=True)
    priority = Column(SAEnum(ComplaintPriority), default=ComplaintPriority.medium)
    status = Column(SAEnum(ComplaintStatus), default=ComplaintStatus.new)

    # Location
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    address = Column(String(300), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_source = Column(String(20), default="user_entered")  # gps|user_entered|demo

    # Routing
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    routing_reason = Column(Text, nullable=True)

    # AI metadata
    ai_confidence = Column(Float, nullable=True)
    ai_provider = Column(String(30), nullable=True)
    requires_route_optimization = Column(Boolean, default=False)

    # Demo flag
    is_demo_data = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    citizen = relationship("User", back_populates="complaints", foreign_keys=[citizen_id])
    ward = relationship("Ward", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    agent_logs = relationship("AgentLog", back_populates="complaint")


# ── WasteBin ───────────────────────────────────────────────────────────────

class WasteBin(Base):
    __tablename__ = "waste_bins"

    id = Column(Integer, primary_key=True, index=True)
    bin_code = Column(String(20), unique=True, nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(300), nullable=True)
    capacity_liters = Column(Float, default=240.0)
    fill_level_pct = Column(Float, default=0.0)  # 0–100
    waste_category = Column(SAEnum(WasteCategory), default=WasteCategory.dry)
    is_overflow = Column(Boolean, default=False)
    last_collected = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_demo_data = Column(Boolean, default=False)

    ward = relationship("Ward", back_populates="bins")
    route_stops = relationship("RouteStop", back_populates="bin")


# ── Vehicle ────────────────────────────────────────────────────────────────

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(String(50), default="compactor_truck")
    capacity_liters = Column(Float, default=5000.0)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    is_available = Column(Boolean, default=True)
    is_demo_data = Column(Boolean, default=False)

    routes = relationship("CollectionRoute", back_populates="vehicle")


# ── CollectionRoute ────────────────────────────────────────────────────────

class CollectionRoute(Base):
    __tablename__ = "collection_routes"

    id = Column(Integer, primary_key=True, index=True)
    route_code = Column(String(20), unique=True, nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    status = Column(String(20), default="planned")  # planned|active|completed
    total_distance_km = Column(Float, nullable=True)
    estimated_duration_min = Column(Float, nullable=True)
    optimization_algorithm = Column(String(50), default="nearest_neighbor")
    is_demo_data = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", back_populates="routes")
    stops = relationship("RouteStop", back_populates="route", order_by="RouteStop.stop_order")


# ── RouteStop ──────────────────────────────────────────────────────────────

class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("collection_routes.id"), nullable=False)
    bin_id = Column(Integer, ForeignKey("waste_bins.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)
    distance_from_prev_km = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    route = relationship("CollectionRoute", back_populates="stops")
    bin = relationship("WasteBin", back_populates="route_stops")


# ── SegregationRecord ──────────────────────────────────────────────────────

class SegregationRecord(Base):
    __tablename__ = "segregation_records"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    is_compliant = Column(Boolean, default=True)
    waste_category = Column(SAEnum(WasteCategory), nullable=True)
    notes = Column(Text, nullable=True)
    is_demo_data = Column(Boolean, default=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)


# ── AgentLog ───────────────────────────────────────────────────────────────

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=True)
    agent_name = Column(String(50), nullable=False)
    event = Column(String(200), nullable=False)
    detail = Column(Text, nullable=True)
    ai_provider = Column(String(30), nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="agent_logs")


# ── AIRequest ──────────────────────────────────────────────────────────────

class AIRequest(Base):
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(30), nullable=False)
    model = Column(String(80), nullable=False)
    task = Column(String(80), nullable=False)
    success = Column(Boolean, default=True)
    latency_ms = Column(Float, nullable=True)
    fallback_used = Column(Boolean, default=False)
    error_type = Column(String(100), nullable=True)
    # NOTE: never log prompt content containing citizen data
    created_at = Column(DateTime, default=datetime.utcnow)
