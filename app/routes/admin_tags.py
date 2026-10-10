from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query, Response
from fastapi.responses import HTMLResponse
from app.database import get_db
from app.models import QRTagCreate, QRTagAssignRequest, QRTagUpdate
from app.security import get_current_admin, require_roles
from app.id_generator import generate_tag_uid, generate_secure_token
from app.qr_service import (
    get_tag_url,
    generate_qr_png_bytes,
    generate_qr_data_url,
    generate_printable_badge_html,
)

router = APIRouter(prefix="/api/admin/tags", tags=["Admin - QR Tags"])

@router.get("", summary="List QR Tags (Admin)")
async def list_qr_tags(
    status_filter: Optional[str] = None,
    assigned: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT t.id, t.tag_uid, t.status, t.created_at, t.updated_at,
                   a.id as assignment_id, a.assigned_at,
                   d.id as dog_id, d.dog_uid, d.name as dog_name, d.status as dog_status
            FROM qr_tags t
            LEFT JOIN dog_tag_assignments a ON a.tag_id = t.id AND a.status = 'ACTIVE'
            LEFT JOIN dogs d ON a.dog_id = d.id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND t.status = ?"
            params.append(status_filter)
        if assigned is True:
            query += " AND a.id IS NOT NULL"
        elif assigned is False:
            query += " AND a.id IS NULL"
        if search:
            query += " AND (t.tag_uid LIKE ? OR d.name LIKE ? OR d.dog_uid LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])

        query += " ORDER BY t.id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        tag_list = []
        for r in rows:
            tag_list.append({
                "id": r["id"],
                "tag_uid": r["tag_uid"],
                "status": r["status"],
                "qr_url": get_tag_url(r["tag_uid"]),
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
                "current_assignment": {
                    "assignment_id": r["assignment_id"],
                    "dog_id": r["dog_id"],
                    "dog_uid": r["dog_uid"],
                    "dog_name": r["dog_name"],
                    "dog_status": r["dog_status"],
                    "assigned_at": r["assigned_at"],
                } if r["assignment_id"] else None,
            })

        return {
            "limit": limit,
            "offset": offset,
            "tags": tag_list,
        }

@router.post("", status_code=status.HTTP_201_CREATED, summary="Create Physical QR Tag")
async def create_qr_tag(
    payload: QRTagCreate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """
    Generate a new physical QR tag (Section 15):
    - Unique Tag UID (e.g. CU-TAG-8F42K9)
    - Cryptographically secure unique token
    - Static QR URL (/t/CU-TAG-8F42K9)
    - Optional immediate dog assignment
    """
    with get_db() as conn:
        cursor = conn.cursor()
        tag_uid = generate_tag_uid(conn)
        qr_token = generate_secure_token()

        cursor.execute("""
            INSERT INTO qr_tags (tag_uid, qr_token, status)
            VALUES (?, ?, ?)
        """, (tag_uid, qr_token, payload.status))
        tag_id = cursor.lastrowid

        assigned_dog = None
        if payload.assign_to_dog_id:
            cursor.execute("SELECT id, dog_uid, name FROM dogs WHERE id = ?", (payload.assign_to_dog_id,))
            dog = cursor.fetchone()
            if not dog:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified dog does not exist.")

            # Supersede any previous active assignment for this dog or tag
            now_sql = "CURRENT_TIMESTAMP"
            cursor.execute("UPDATE dog_tag_assignments SET status = 'SUPERSEDED', unassigned_at = CURRENT_TIMESTAMP WHERE tag_id = ? AND status = 'ACTIVE'", (tag_id,))
            cursor.execute("UPDATE dog_tag_assignments SET status = 'SUPERSEDED', unassigned_at = CURRENT_TIMESTAMP WHERE dog_id = ? AND status = 'ACTIVE'", (dog["id"],))

            cursor.execute("""
                INSERT INTO dog_tag_assignments (dog_id, tag_id, assigned_by, status)
                VALUES (?, ?, ?, 'ACTIVE')
            """, (dog["id"], tag_id, current_user["id"]))

            assigned_dog = {
                "dog_id": dog["id"],
                "dog_uid": dog["dog_uid"],
                "dog_name": dog["name"],
            }

        return {
            "id": tag_id,
            "tag_uid": tag_uid,
            "qr_token": qr_token,
            "status": payload.status,
            "qr_url": get_tag_url(tag_uid),
            "assigned_dog": assigned_dog,
            "qr_data_url": generate_qr_data_url(tag_uid, box_size=6),
        }

@router.get("/{tag_id}", summary="Get Tag Details & History")
async def get_tag_details(
    tag_id: int,
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qr_tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

        # Active assignment
        cursor.execute("""
            SELECT a.*, d.dog_uid, d.name as dog_name, d.status as dog_status
            FROM dog_tag_assignments a
            JOIN dogs d ON a.dog_id = d.id
            WHERE a.tag_id = ? AND a.status = 'ACTIVE'
            LIMIT 1
        """, (tag_id,))
        active_assignment = cursor.fetchone()

        # Full assignment history
        cursor.execute("""
            SELECT a.*, d.dog_uid, d.name as dog_name, u.name as assigned_by_name
            FROM dog_tag_assignments a
            JOIN dogs d ON a.dog_id = d.id
            LEFT JOIN admin_users u ON a.assigned_by = u.id
            WHERE a.tag_id = ?
            ORDER BY a.assigned_at DESC
        """, (tag_id,))
        history = [dict(r) for r in cursor.fetchall()]

        return {
            "id": tag["id"],
            "tag_uid": tag["tag_uid"],
            "qr_token": tag["qr_token"],
            "status": tag["status"],
            "qr_url": get_tag_url(tag["tag_uid"]),
            "current_assignment": dict(active_assignment) if active_assignment else None,
            "history": history,
            "qr_data_url": generate_qr_data_url(tag["tag_uid"]),
        }

@router.patch("/{tag_id}", summary="Update Tag Status (Admin)")
async def update_tag_status(
    tag_id: int,
    payload: QRTagUpdate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """Update physical tag status: ACTIVE, INACTIVE, LOST, DAMAGED, RETIRED."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qr_tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

        if payload.status:
            cursor.execute("UPDATE qr_tags SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (payload.status, tag_id))

        cursor.execute("SELECT * FROM qr_tags WHERE id = ?", (tag_id,))
        return dict(cursor.fetchone())

@router.post("/{tag_id}/assign", summary="Assign Tag to Dog")
async def assign_tag_to_dog(
    tag_id: int,
    payload: QRTagAssignRequest,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """
    CRITICAL WORKFLOW (Sections 8, 16, 47 Test 3 & 12):
    Assign a physical QR tag to a specific dog.
    - If tag already assigned, mark old assignment SUPERSEDED with unassigned_at timestamp.
    - If dog already has another tag, mark old assignment SUPERSEDED.
    - Create new active assignment.
    - Preserves complete historical audit trail!
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qr_tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

        cursor.execute("SELECT * FROM dogs WHERE id = ?", (payload.dog_id,))
        dog = cursor.fetchone()
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")

        # Supersede any existing active assignment for this tag
        cursor.execute("""
            UPDATE dog_tag_assignments
            SET status = 'SUPERSEDED', unassigned_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE tag_id = ? AND status = 'ACTIVE'
        """, (tag_id,))

        # Supersede any existing active assignment for this dog
        cursor.execute("""
            UPDATE dog_tag_assignments
            SET status = 'SUPERSEDED', unassigned_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE dog_id = ? AND status = 'ACTIVE'
        """, (payload.dog_id,))

        # Insert new active assignment
        cursor.execute("""
            INSERT INTO dog_tag_assignments (dog_id, tag_id, assigned_by, status)
            VALUES (?, ?, ?, 'ACTIVE')
        """, (payload.dog_id, tag_id, current_user["id"]))

        assignment_id = cursor.lastrowid

        return {
            "status": "SUCCESS",
            "message": f"Tag {tag['tag_uid']} successfully assigned to {dog['name']} ({dog['dog_uid']}).",
            "assignment_id": assignment_id,
            "tag_uid": tag["tag_uid"],
            "dog_uid": dog["dog_uid"],
            "dog_name": dog["name"],
        }

@router.post("/{tag_id}/unassign", summary="Unassign Tag from Dog")
async def unassign_tag_from_dog(
    tag_id: int,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    """
    Unassign tag (Section 47 Test 11):
    - Closes active assignment with unassigned_at timestamp.
    - Preserves historical assignment.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qr_tags WHERE id = ?", (tag_id,))
        tag = cursor.fetchone()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

        cursor.execute("""
            SELECT a.id, d.name as dog_name, d.dog_uid
            FROM dog_tag_assignments a
            JOIN dogs d ON a.dog_id = d.id
            WHERE a.tag_id = ? AND a.status = 'ACTIVE'
        """, (tag_id,))
        active_assignment = cursor.fetchone()

        if not active_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag {tag['tag_uid']} does not have an active dog assignment.",
            )

        cursor.execute("""
            UPDATE dog_tag_assignments
            SET status = 'UNASSIGNED', unassigned_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (active_assignment["id"],))

        return {
            "status": "SUCCESS",
            "message": f"Tag {tag['tag_uid']} has been unassigned from {active_assignment['dog_name']} ({active_assignment['dog_uid']}).",
            "tag_uid": tag["tag_uid"],
        }

@router.get("/{tag_id}/history", summary="Get Tag Assignment History")
async def get_tag_history(
    tag_id: int,
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.dog_id, d.dog_uid, d.name as dog_name,
                   a.assigned_at, a.unassigned_at, a.status,
                   u.name as assigned_by_name
            FROM dog_tag_assignments a
            JOIN dogs d ON a.dog_id = d.id
            LEFT JOIN admin_users u ON a.assigned_by = u.id
            WHERE a.tag_id = ?
            ORDER BY a.assigned_at DESC
        """, (tag_id,))
        return [dict(r) for r in cursor.fetchall()]

@router.get("/{tag_id}/qr-image", summary="Download QR Code PNG Image")
async def get_qr_image(tag_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tag_uid FROM qr_tags WHERE id = ?", (tag_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

        png_bytes = generate_qr_png_bytes(row["tag_uid"])
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=\"qr_{row['tag_uid']}.png\""}
        )

@router.get("/{tag_id}/printable-badge", summary="Printable Collar Tag Badge")
async def get_printable_badge(tag_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.tag_uid, d.dog_uid, d.name as dog_name
            FROM qr_tags t
            LEFT JOIN dog_tag_assignments a ON a.tag_id = t.id AND a.status = 'ACTIVE'
            LEFT JOIN dogs d ON a.dog_id = d.id
            WHERE t.id = ?
        """, (tag_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

        html = generate_printable_badge_html(
            tag_uid=row["tag_uid"],
            dog_name=row["dog_name"],
            dog_uid=row["dog_uid"],
        )
        return HTMLResponse(content=html)
