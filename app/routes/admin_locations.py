from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_db
from app.models import CampusLocationCreate, CampusLocationUpdate
from app.security import get_current_admin, require_roles

router = APIRouter(prefix="/api/admin/locations", tags=["Admin - Locations"])

@router.get("", summary="List All Campus Locations (Admin)")
async def list_locations(current_user: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM campus_locations ORDER BY area_type, name")
        return [dict(r) for r in cursor.fetchall()]

@router.post("", status_code=status.HTTP_201_CREATED, summary="Add Campus Location")
async def add_location(
    payload: CampusLocationCreate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO campus_locations (name, description, latitude, longitude, area_type, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload.name.strip(),
            payload.description,
            payload.latitude,
            payload.longitude,
            payload.area_type,
            1 if payload.is_active else 0,
        ))
        loc_id = cursor.lastrowid
        cursor.execute("SELECT * FROM campus_locations WHERE id = ?", (loc_id,))
        return dict(cursor.fetchone())

@router.patch("/{location_id}", summary="Update Campus Location")
async def update_location(
    location_id: int,
    payload: CampusLocationUpdate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM campus_locations WHERE id = ?", (location_id,))
        loc = cursor.fetchone()
        if not loc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campus location not found.")

        fields = []
        values = []
        if payload.name is not None:
            fields.append("name = ?")
            values.append(payload.name.strip())
        if payload.description is not None:
            fields.append("description = ?")
            values.append(payload.description)
        if payload.latitude is not None:
            fields.append("latitude = ?")
            values.append(payload.latitude)
        if payload.longitude is not None:
            fields.append("longitude = ?")
            values.append(payload.longitude)
        if payload.area_type is not None:
            fields.append("area_type = ?")
            values.append(payload.area_type)
        if payload.is_active is not None:
            fields.append("is_active = ?")
            values.append(1 if payload.is_active else 0)

        if fields:
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(location_id)
            cursor.execute(f"UPDATE campus_locations SET {', '.join(fields)} WHERE id = ?", values)

        cursor.execute("SELECT * FROM campus_locations WHERE id = ?", (location_id,))
        return dict(cursor.fetchone())
