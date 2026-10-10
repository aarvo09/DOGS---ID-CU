from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.database import get_db
from app.security import get_current_admin, require_roles
from app.utils import format_time_ago

router = APIRouter(prefix="/api/admin/sightings", tags=["Admin - Sightings"])

class SightingModerationUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(ACTIVE|FLAGGED|REMOVED)$")
    is_verified: Optional[bool] = None

@router.get("", summary="List All Sightings with Telemetry (Admin)")
async def list_admin_sightings(
    dog_id: Optional[int] = None,
    location_id: Optional[int] = None,
    source: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT s.*, d.dog_uid, d.name as dog_name, cl.name as campus_loc_name
            FROM sightings s
            JOIN dogs d ON s.dog_id = d.id
            LEFT JOIN campus_locations cl ON s.location_id = cl.id
            WHERE 1=1
        """
        params = []
        if dog_id:
            query += " AND s.dog_id = ?"
            params.append(dog_id)
        if location_id:
            query += " AND s.location_id = ?"
            params.append(location_id)
        if source:
            query += " AND s.source = ?"
            params.append(source)
        if status_filter:
            query += " AND s.status = ?"
            params.append(status_filter)

        query += " ORDER BY s.created_at DESC, s.id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            loc = r["campus_loc_name"] or r["location_name"] or "Campus Grounds"
            item = dict(r)
            item["resolved_location"] = loc
            item["time_ago"] = format_time_ago(r["created_at"])
            results.append(item)

        return {
            "limit": limit,
            "offset": offset,
            "sightings": results,
        }

@router.get("/{sighting_id}", summary="Get Single Sighting (Admin)")
async def get_sighting_detail(
    sighting_id: int,
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, d.dog_uid, d.name as dog_name, cl.name as campus_loc_name
            FROM sightings s
            JOIN dogs d ON s.dog_id = d.id
            LEFT JOIN campus_locations cl ON s.location_id = cl.id
            WHERE s.id = ?
        """, (sighting_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sighting not found.")

        item = dict(row)
        item["resolved_location"] = row["campus_loc_name"] or row["location_name"] or "Campus Grounds"
        item["time_ago"] = format_time_ago(row["created_at"])
        return item

@router.patch("/{sighting_id}", summary="Moderate Sighting (Flag / Remove / Verify)")
async def moderate_sighting(
    sighting_id: int,
    payload: SightingModerationUpdate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """
    Moderation capability (Section 36):
    Admins can flag spam, mark unverified, or remove abusive sightings.
    Removed/Flagged sightings are instantly excluded from public last-spotted resolution.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sightings WHERE id = ?", (sighting_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sighting not found.")

        fields = []
        values = []
        if payload.status is not None:
            fields.append("status = ?")
            values.append(payload.status)
        if payload.is_verified is not None:
            fields.append("is_verified = ?")
            values.append(1 if payload.is_verified else 0)

        if fields:
            values.append(sighting_id)
            cursor.execute(f"UPDATE sightings SET {', '.join(fields)} WHERE id = ?", values)

        cursor.execute("SELECT * FROM sightings WHERE id = ?", (sighting_id,))
        return dict(cursor.fetchone())
