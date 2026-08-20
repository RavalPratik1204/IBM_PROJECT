"""Admin API — users, wards, departments, system config."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User, Ward, Department, UserRole

router = APIRouter()


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    users = db.query(User).all()
    return [
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role.value, "is_active": u.is_active}
        for u in users
    ]


@router.get("/wards")
def list_wards(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    wards = db.query(Ward).all()
    return [
        {
            "id": w.id, "name": w.name, "code": w.code,
            "latitude": w.latitude, "longitude": w.longitude,
            "population": w.population, "is_active": w.is_active
        }
        for w in wards
    ]


@router.get("/departments")
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("officer", "admin")),
):
    depts = db.query(Department).all()
    return [
        {"id": d.id, "name": d.name, "code": d.code, "description": d.description}
        for d in depts
    ]


class WardCreate(BaseModel):
    name: str
    code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None


@router.post("/wards")
def create_ward(
    req: WardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    if db.query(Ward).filter(Ward.code == req.code).first():
        raise HTTPException(status_code=400, detail="Ward code already exists")
    ward = Ward(**req.dict())
    db.add(ward)
    db.commit()
    db.refresh(ward)
    return {"id": ward.id, "name": ward.name, "code": ward.code}
