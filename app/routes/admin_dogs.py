from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.database import get_db
from app.models import (
    DogCreate,
    DogUpdate,
    HealthRecordCreate,
    HealthRecordUpdate,
)
from app.security import get_current_admin, require_roles
from app.id_generator import generate_dog_uid
from app.utils import format_time_ago, resolve_last_seen_for_dog, resolve_active_tag_for_dog

router = APIRouter(prefix="/api/admin/dogs", tags=["Admin - Dogs"])

@router.get("", summary="List All Campus Dogs (Admin)")
async def list_admin_dogs(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin),
):
    """List dogs with status filter, text search, active tag, and stats."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT d.*, 
                   t.tag_uid as active_tag_uid,
                   (SELECT COUNT(*) FROM sightings WHERE dog_id = d.id) as sightings_count,
                   (SELECT COUNT(*) FROM reports WHERE dog_id = d.id AND status = 'PENDING') as open_reports_count,
                   (SELECT health_status FROM dog_health_records WHERE dog_id = d.id ORDER BY id DESC LIMIT 1) as health_status
            FROM dogs d
            LEFT JOIN dog_tag_assignments a ON a.dog_id = d.id AND a.status = 'ACTIVE'
            LEFT JOIN qr_tags t ON a.tag_id = t.id AND t.status = 'ACTIVE'
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND d.status = ?"
            params.append(status_filter)
        if search:
            query += " AND (d.name LIKE ? OR d.dog_uid LIKE ? OR d.description LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])

        query += " ORDER BY d.id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Total count query
        count_query = "SELECT COUNT(*) as total FROM dogs WHERE 1=1"
        count_params = []
        if status_filter:
            count_query += " AND status = ?"
            count_params.append(status_filter)
        if search:
            count_query += " AND (name LIKE ? OR dog_uid LIKE ? OR description LIKE ?)"
            count_params.extend([f"%{search.strip()}%", f"%{search.strip()}%", f"%{search.strip()}%"])
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()["total"]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "dogs": [dict(r) for r in rows],
        }

@router.post("", status_code=status.HTTP_201_CREATED, summary="Register New Campus Dog")
async def create_dog(
    payload: DogCreate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """
    Register a new campus dog with an auto-generated or custom validated Dog ID.
    Section 14: System generates CU-DOG-XXX to prevent conflicting IDs.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            dog_uid = generate_dog_uid(conn, requested_uid=payload.dog_uid)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        cursor.execute("""
            INSERT INTO dogs (dog_uid, name, gender, approx_age, description, photo_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dog_uid,
            payload.name.strip(),
            payload.gender,
            payload.approx_age.strip(),
            payload.description,
            payload.photo_url,
            payload.status,
        ))
        new_id = cursor.lastrowid

        # Insert default health record placeholder
        cursor.execute("""
            INSERT INTO dog_health_records (dog_id, vaccination_status, sterilization_status, health_status, updated_by)
            VALUES (?, 'UNKNOWN', 'UNKNOWN', 'HEALTHY', ?)
        """, (new_id, current_user["id"]))

        cursor.execute("SELECT * FROM dogs WHERE id = ?", (new_id,))
        created_dog = cursor.fetchone()
        return dict(created_dog)

@router.get("/{dog_id}", summary="Get Full Dog Details (Admin)")
async def get_admin_dog_details(
    dog_id: int,
    current_user: dict = Depends(get_current_admin),
):
    """Retrieve full operational dossier on a dog including assignments, health, sightings, and reports."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dogs WHERE id = ?", (dog_id,))
        dog = cursor.fetchone()
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")

        # Tag history
        cursor.execute("""
            SELECT a.id, a.tag_id, t.tag_uid, t.status as tag_status,
                   a.assigned_at, a.unassigned_at, a.status as assignment_status,
                   u.name as assigned_by_name
            FROM dog_tag_assignments a
            JOIN qr_tags t ON a.tag_id = t.id
            LEFT JOIN admin_users u ON a.assigned_by = u.id
            WHERE a.dog_id = ?
            ORDER BY a.assigned_at DESC
        """, (dog_id,))
        tag_assignments = [dict(r) for r in cursor.fetchall()]

        # Health records
        cursor.execute("""
            SELECT h.*, u.name as updated_by_name
            FROM dog_health_records h
            LEFT JOIN admin_users u ON h.updated_by = u.id
            WHERE h.dog_id = ?
            ORDER BY h.id DESC
        """, (dog_id,))
        health_records = [dict(r) for r in cursor.fetchall()]

        # Recent sightings
        cursor.execute("""
            SELECT s.*, cl.name as campus_loc_name
            FROM sightings s
            LEFT JOIN campus_locations cl ON s.location_id = cl.id
            WHERE s.dog_id = ?
            ORDER BY s.created_at DESC
            LIMIT 20
        """, (dog_id,))
        recent_sightings = [dict(r) for r in cursor.fetchall()]

        # Reports
        cursor.execute("""
            SELECT r.*, cl.name as campus_loc_name, u.name as resolved_by_name
            FROM reports r
            LEFT JOIN campus_locations cl ON r.location_id = cl.id
            LEFT JOIN admin_users u ON r.resolved_by = u.id
            WHERE r.dog_id = ?
            ORDER BY r.created_at DESC
        """, (dog_id,))
        reports = [dict(r) for r in cursor.fetchall()]

        last_seen = resolve_last_seen_for_dog(conn, dog_id)

        dog_dict = dict(dog)
        dog_dict["last_seen"] = last_seen
        dog_dict["tag_assignments"] = tag_assignments
        dog_dict["health_records"] = health_records
        dog_dict["recent_sightings"] = recent_sightings
        dog_dict["reports"] = reports
        return dog_dict

@router.patch("/{dog_id}", summary="Update Dog Master Information")
async def update_dog_info(
    dog_id: int,
    payload: DogUpdate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """
    Update official dog master information.
    CRITICAL: Updating dog info does NOT alter the QR code or its assignment.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dogs WHERE id = ?", (dog_id,))
        dog = cursor.fetchone()
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")

        fields = []
        values = []
        if payload.name is not None:
            fields.append("name = ?")
            values.append(payload.name.strip())
        if payload.gender is not None:
            fields.append("gender = ?")
            values.append(payload.gender)
        if payload.approx_age is not None:
            fields.append("approx_age = ?")
            values.append(payload.approx_age.strip())
        if payload.description is not None:
            fields.append("description = ?")
            values.append(payload.description)
        if payload.photo_url is not None:
            fields.append("photo_url = ?")
            values.append(payload.photo_url)
        if payload.status is not None:
            fields.append("status = ?")
            values.append(payload.status)

        if not fields:
            return dict(dog)

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(dog_id)

        sql = f"UPDATE dogs SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(sql, values)

        cursor.execute("SELECT * FROM dogs WHERE id = ?", (dog_id,))
        return dict(cursor.fetchone())

@router.delete("/{dog_id}", summary="Deactivate Dog (Soft-Delete)")
async def deactivate_dog(
    dog_id: int,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """Set dog status to INACTIVE. Historical records are preserved per Section 40."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dogs WHERE id = ?", (dog_id,))
        dog = cursor.fetchone()
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")

        cursor.execute("UPDATE dogs SET status = 'INACTIVE', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (dog_id,))
        return {"status": "SUCCESS", "message": f"Dog '{dog['name']}' ({dog['dog_uid']}) has been marked INACTIVE."}

# --- Health Record Sub-endpoints ---
@router.get("/{dog_id}/health", summary="Get Dog Health Records")
async def get_dog_health_records(
    dog_id: int,
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.*, u.name as updated_by_name
            FROM dog_health_records h
            LEFT JOIN admin_users u ON h.updated_by = u.id
            WHERE h.dog_id = ?
            ORDER BY h.id DESC
        """, (dog_id,))
        return [dict(r) for r in cursor.fetchall()]

@router.post("/{dog_id}/health", status_code=status.HTTP_201_CREATED, summary="Add Dog Health Record")
async def add_dog_health_record(
    dog_id: int,
    payload: HealthRecordCreate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM dogs WHERE id = ?", (dog_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")

        cursor.execute("""
            INSERT INTO dog_health_records (
                dog_id, vaccination_status, last_vaccination_date, sterilization_status, health_status, notes, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dog_id,
            payload.vaccination_status,
            payload.last_vaccination_date,
            payload.sterilization_status,
            payload.health_status,
            payload.notes,
            current_user["id"],
        ))
        record_id = cursor.lastrowid
        cursor.execute("SELECT * FROM dog_health_records WHERE id = ?", (record_id,))
        return dict(cursor.fetchone())

@router.patch("/{dog_id}/health/{record_id}", summary="Update Dog Health Record")
async def update_dog_health_record(
    dog_id: int,
    record_id: int,
    payload: HealthRecordUpdate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dog_health_records WHERE id = ? AND dog_id = ?", (record_id, dog_id))
        rec = cursor.fetchone()
        if not rec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found.")

        fields = []
        values = []
        if payload.vaccination_status is not None:
            fields.append("vaccination_status = ?")
            values.append(payload.vaccination_status)
        if payload.last_vaccination_date is not None:
            fields.append("last_vaccination_date = ?")
            values.append(payload.last_vaccination_date)
        if payload.sterilization_status is not None:
            fields.append("sterilization_status = ?")
            values.append(payload.sterilization_status)
        if payload.health_status is not None:
            fields.append("health_status = ?")
            values.append(payload.health_status)
        if payload.notes is not None:
            fields.append("notes = ?")
            values.append(payload.notes)

        if fields:
            fields.append("updated_by = ?")
            values.append(current_user["id"])
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(record_id)
            cursor.execute(f"UPDATE dog_health_records SET {', '.join(fields)} WHERE id = ?", values)

        cursor.execute("SELECT * FROM dog_health_records WHERE id = ?", (record_id,))
        return dict(cursor.fetchone())
