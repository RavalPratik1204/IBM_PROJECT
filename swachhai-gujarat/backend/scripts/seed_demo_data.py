"""
Demo Data Seeder -- generates realistic synthetic data for SwachhAI Gujarat.
CLEARLY LABELED: Synthetic Demo Data -- Not Official Municipal Data

Run: python scripts/seed_demo_data.py
"""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import (
    User, Ward, Department, Complaint, WasteBin, Vehicle,
    CollectionRoute, RouteStop, SegregationRecord, AgentLog,
    UserRole, ComplaintStatus, ComplaintPriority, WasteCategory
)

Base.metadata.create_all(bind=engine)

DEMO_LABEL = True  # All records marked as demo data

# ── Ahmedabad-inspired ward data ────────────────────────────────────────────
WARD_DATA = [
    {"name": "Navrangpura", "code": "W01", "lat": 23.0368, "lon": 72.5614, "pop": 45000},
    {"name": "Ellisbridge",  "code": "W02", "lat": 23.0225, "lon": 72.5710, "pop": 38000},
    {"name": "Maninagar",   "code": "W03", "lat": 22.9913, "lon": 72.6058, "pop": 52000},
    {"name": "Satellite",   "code": "W04", "lat": 23.0168, "lon": 72.5280, "pop": 41000},
    {"name": "Bodakdev",    "code": "W05", "lat": 23.0489, "lon": 72.5110, "pop": 36000},
    {"name": "Gota",        "code": "W06", "lat": 23.1017, "lon": 72.5308, "pop": 58000},
    {"name": "Vastral",     "code": "W07", "lat": 22.9992, "lon": 72.6502, "pop": 63000},
    {"name": "Nikol",       "code": "W08", "lat": 23.0358, "lon": 72.6408, "pop": 71000},
    {"name": "Chandkheda",  "code": "W09", "lat": 23.1063, "lon": 72.5877, "pop": 48000},
    {"name": "Naroda",      "code": "W10", "lat": 23.0769, "lon": 72.6525, "pop": 55000},
]

DEPT_DATA = [
    {"name": "Waste Collection Department", "code": "WASTE_COLLECTION",
     "description": "Handles garbage collection, pickups and schedules"},
    {"name": "Sanitation Department", "code": "SANITATION",
     "description": "Manages cleanliness, illegal dumping and roadside garbage"},
    {"name": "Recycling Department", "code": "RECYCLING",
     "description": "Manages recycling collection and processing"},
    {"name": "Segregation Department", "code": "SEGREGATION",
     "description": "Promotes and monitors waste segregation compliance"},
    {"name": "General Services", "code": "GENERAL",
     "description": "Handles general waste-related service requests"},
]

COMPLAINT_TEMPLATES = [
    ("waste_collection", "hi",  "मेरे इलाके में तीन दिनों से कचरा नहीं उठाया गया है।", "high"),
    ("waste_collection", "gu",  "મારા વિસ્તારમાં ત્રણ દિવસથી કચરો ઉપાડવામાં આવ્યો નથી.", "high"),
    ("waste_collection", "en",  "Garbage has not been picked up for 3 days.", "high"),
    ("overflow_bin",     "en",  "The waste bin near the market is overflowing.", "critical"),
    ("overflow_bin",     "hi",  "बाजार के पास का कचरा पात्र भर गया है।", "critical"),
    ("illegal_dumping",  "en",  "Someone has dumped garbage illegally near the park.", "medium"),
    ("illegal_dumping",  "gu",  "પાર્ક નજીક ગેરકાયદે કચરો ફેંકવામાં આવ્યો છે.", "medium"),
    ("roadside_garbage", "en",  "There is a lot of garbage on the main road.", "medium"),
    ("segregation_issue","en",  "People are mixing wet and dry waste in our building.", "low"),
    ("recycling_issue",  "en",  "Recyclable waste is not being collected separately.", "low"),
    ("schedule_issue",   "hi",  "कचरा उठाने का समय बदल गया है, कोई सूचना नहीं दी गई।", "low"),
    ("waste_collection", "en",  "No collection for 2 days. Very bad smell.", "high"),
    ("overflow_bin",     "en",  "Bin at bus stop is completely full, hazard to public.", "critical"),
    ("illegal_dumping",  "en",  "Construction debris dumped on residential street.", "high"),
    ("waste_collection", "gu",  "કચરો ઉઠાવવામાં ખૂબ વિલંબ થઈ રહ્યો છે.", "medium"),
]

STATUS_POOL = [
    ComplaintStatus.new, ComplaintStatus.assigned,
    ComplaintStatus.in_progress, ComplaintStatus.resolved,
    ComplaintStatus.resolved, ComplaintStatus.resolved,  # more resolved for realistic stats
]


def seed():
    db = SessionLocal()
    print("[WARNING] SYNTHETIC DEMO DATA -- Not Official Municipal Data\n")

    # ── Users ──────────────────────────────────────────────────────────────
    print("Creating users...")
    admin = User(name="Admin User", email="admin@swachhai.demo",
                 password_hash=hash_password("admin123"), role=UserRole.admin,
                 preferred_language="en")
    officer = User(name="Officer Patel", email="officer@swachhai.demo",
                   password_hash=hash_password("officer123"), role=UserRole.officer,
                   preferred_language="gu")
    db.add_all([admin, officer])
    db.flush()

    citizens = []
    for i in range(1, 11):
        lang = random.choice(["en", "hi", "gu"])
        c = User(
            name=f"Citizen {i}", email=f"citizen{i}@demo.swachhai",
            password_hash=hash_password("citizen123"), role=UserRole.citizen,
            preferred_language=lang,
        )
        db.add(c)
        citizens.append(c)
    db.flush()

    # ── Wards ──────────────────────────────────────────────────────────────
    print("Creating wards...")
    wards = []
    for wd in WARD_DATA:
        w = Ward(name=wd["name"], code=wd["code"], city="Ahmedabad",
                 latitude=wd["lat"], longitude=wd["lon"], population=wd["pop"])
        db.add(w)
        wards.append(w)
    db.flush()

    # ── Departments ────────────────────────────────────────────────────────
    print("Creating departments...")
    depts = {}
    for dd in DEPT_DATA:
        dept = Department(name=dd["name"], code=dd["code"], description=dd["description"])
        db.add(dept)
        db.flush()
        depts[dd["code"]] = dept

    # ── Waste Bins ─────────────────────────────────────────────────────────
    print("Creating 50 waste bins...")
    bins = []
    for i, ward in enumerate(wards):
        for j in range(5):  # 5 bins per ward = 50 total
            lat_offset = random.uniform(-0.005, 0.005)
            lon_offset = random.uniform(-0.005, 0.005)
            fill = random.uniform(10, 100)
            b = WasteBin(
                bin_code=f"BIN-{ward.code}-{j+1:02d}",
                ward_id=ward.id,
                latitude=ward.latitude + lat_offset,
                longitude=ward.longitude + lon_offset,
                address=f"Near landmark {j+1}, {ward.name}",
                capacity_liters=240,
                fill_level_pct=round(fill, 1),
                waste_category=random.choice(list(WasteCategory)),
                is_overflow=(fill > 90),
                is_demo_data=True,
            )
            db.add(b)
            bins.append(b)
    db.flush()

    # ── Vehicles ───────────────────────────────────────────────────────────
    print("Creating 10 vehicles...")
    vehicles = []
    for i, ward in enumerate(wards):
        v = Vehicle(
            vehicle_number=f"GJ01-ZZ-{1000+i}",
            vehicle_type="compactor_truck",
            capacity_liters=5000,
            ward_id=ward.id,
            is_available=True,
            is_demo_data=True,
        )
        db.add(v)
        vehicles.append(v)
    db.flush()

    # ── Complaints ─────────────────────────────────────────────────────────
    print("Creating 200 complaints...")
    category_dept = {
        "waste_collection": "WASTE_COLLECTION",
        "overflow_bin": "WASTE_COLLECTION",
        "illegal_dumping": "SANITATION",
        "roadside_garbage": "SANITATION",
        "segregation_issue": "SEGREGATION",
        "recycling_issue": "RECYCLING",
        "schedule_issue": "WASTE_COLLECTION",
        "other": "GENERAL",
    }

    for i in range(200):
        tmpl = COMPLAINT_TEMPLATES[i % len(COMPLAINT_TEMPLATES)]
        cat, lang, text, prio = tmpl
        ward = random.choice(wards)
        citizen = random.choice(citizens)
        days_ago = random.randint(0, 60)
        created = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
        status = random.choice(STATUS_POOL)
        dept_code = category_dept.get(cat, "GENERAL")
        dept = depts.get(dept_code)

        resolved_at = None
        if status == ComplaintStatus.resolved:
            resolved_at = created + timedelta(hours=random.randint(4, 72))

        c = Complaint(
            ticket_id=f"SG-{created.strftime('%Y%m%d')}-{i+1:04d}",
            citizen_id=citizen.id,
            citizen_name=citizen.name,
            original_text=text,
            language=lang,
            description=f"[DEMO] {text[:100]}",
            category=cat,
            priority=ComplaintPriority(prio),
            status=status,
            ward_id=ward.id,
            address=f"Demo address, {ward.name}",
            latitude=ward.latitude + random.uniform(-0.005, 0.005),
            longitude=ward.longitude + random.uniform(-0.005, 0.005),
            location_source="demo",
            department_id=dept.id if dept else None,
            routing_reason=f"Auto-routed: category={cat}",
            ai_confidence=round(random.uniform(0.75, 0.98), 2),
            ai_provider=random.choice(["groq", "groq", "ibm", "deterministic_fallback"]),
            requires_route_optimization=(cat in ["waste_collection", "overflow_bin"]),
            is_demo_data=True,
            created_at=created,
            resolved_at=resolved_at,
        )
        db.add(c)

    db.flush()

    # ── Segregation Records ────────────────────────────────────────────────
    print("Creating segregation records...")
    for i in range(150):
        ward = random.choice(wards)
        sr = SegregationRecord(
            citizen_id=random.choice(citizens).id,
            ward_id=ward.id,
            is_compliant=random.random() > 0.3,
            waste_category=random.choice(list(WasteCategory)),
            notes="Demo segregation record",
            is_demo_data=True,
            recorded_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        db.add(sr)

    db.commit()
    print("\n[OK] Demo data seeded successfully!")
    print("   Admin login:   admin@swachhai.demo / admin123")
    print("   Officer login: officer@swachhai.demo / officer123")
    print("   Citizen login: citizen1@demo.swachhai / citizen123")
    print("\n[WARNING] SYNTHETIC DEMO DATA -- Not Official Municipal Data")


if __name__ == "__main__":
    seed()

