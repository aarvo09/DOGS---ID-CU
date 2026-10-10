from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException, status, Query
from app.database import get_db
from app.models import (
    DogPublicResponse,
    SightingCreate,
    SightingPublicResponse,
    ReportCreate,
)
from app.utils import (
    format_time_ago,
    hash_client_ip,
    resolve_last_seen_for_dog,
    resolve_health_overview,
    resolve_active_tag_for_dog,
)
from app.middleware import enforce_public_rate_limit

router = APIRouter(prefix="/api", tags=["Public API"])

@router.get("/locations", summary="List Active Campus Locations")
async def get_active_campus_locations():
    """Returns active Chandigarh University campus locations for location selection."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, latitude, longitude, area_type
            FROM campus_locations
            WHERE is_active = 1
            ORDER BY area_type, name
        """)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.get("/dogs/{dog_uid}", response_model=DogPublicResponse, summary="Get Public Dog Profile")
async def get_public_dog_profile(dog_uid: str):
    """
    Returns public dog profile for students, faculty, and visitors.
    Resolves dynamic last-seen location, public health overview, and active tag.
    Does NOT leak internal IDs, admin notes, or private database structures.
    """
    clean_uid = dog_uid.strip().upper()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, dog_uid, name, gender, approx_age, description, photo_url, status
            FROM dogs
            WHERE dog_uid = ?
        """, (clean_uid,))
        dog = cursor.fetchone()

        if not dog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus dog with ID '{clean_uid}' was not found in the registry.",
            )

        dog_id = dog["id"]
        last_seen = resolve_last_seen_for_dog(conn, dog_id)
        health = resolve_health_overview(conn, dog_id)
        active_tag = resolve_active_tag_for_dog(conn, dog_id)

        return DogPublicResponse(
            dog_uid=dog["dog_uid"],
            name=dog["name"],
            gender=dog["gender"],
            approx_age=dog["approx_age"],
            description=dog["description"],
            photo_url=dog["photo_url"],
            status=dog["status"],
            last_seen=last_seen,
            health_overview=health,
            active_tag=active_tag,
        )

@router.get("/dogs/{dog_uid}/sightings", response_model=List[SightingPublicResponse], summary="Get Sighting History for Dog")
async def get_dog_sightings(
    dog_uid: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Returns chronologically ordered public sightings for a specific dog."""
    clean_uid = dog_uid.strip().upper()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM dogs WHERE dog_uid = ?", (clean_uid,))
        dog = cursor.fetchone()
        if not dog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dog '{clean_uid}' not found.",
            )

        cursor.execute("""
            SELECT s.id, s.location_name, s.activity, s.photo_url, s.note, s.created_at,
                   cl.name as campus_loc_name
            FROM sightings s
            LEFT JOIN campus_locations cl ON s.location_id = cl.id
            WHERE s.dog_id = ? AND s.status = 'ACTIVE' AND s.is_verified = 1
            ORDER BY s.created_at DESC, s.id DESC
            LIMIT ? OFFSET ?
        """, (dog["id"], limit, offset))

        sightings = []
        for r in cursor.fetchall():
            resolved_loc = r["campus_loc_name"] or r["location_name"] or "Campus Grounds"
            sightings.append(SightingPublicResponse(
                id=r["id"],
                dog_uid=clean_uid,
                dog_name=dog["name"],
                location_name=resolved_loc,
                activity=r["activity"],
                photo_url=r["photo_url"],
                note=r["note"],
                time_ago=format_time_ago(r["created_at"]),
                created_at=r["created_at"],
            ))

        return sightings

@router.post("/dogs/{dog_uid}/sightings", status_code=status.HTTP_201_CREATED, summary="Submit a Public Dog Sighting")
async def submit_dog_sighting(
    dog_uid: str,
    payload: SightingCreate,
    request: Request,
):
    """
    Public Sighting Submission (Sections 18-23 & 44-45):
    - Public user reports "I SAW THIS DOG"
    - Validates dog existence
    - Creates a new historical record in the sightings table
    - Automatically updates the dog's dynamically resolved last-seen information
    - Protected by anti-abuse rate limiting and IP hashing
    """
    enforce_public_rate_limit(request, endpoint_type="sightings")
    clean_uid = dog_uid.strip().upper()
    client_ip = request.client.host if request.client else "127.0.0.1"
    hashed_ip = hash_client_ip(client_ip)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status FROM dogs WHERE dog_uid = ?", (clean_uid,))
        dog = cursor.fetchone()
        if not dog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dog '{clean_uid}' not found.",
            )

        if dog["status"] in ("DECEASED", "TRANSFERRED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot report sightings for dog with status '{dog['status']}'.",
            )

        # Resolve location name
        resolved_name = payload.location_name
        if payload.location_id:
            cursor.execute("SELECT name FROM campus_locations WHERE id = ?", (payload.location_id,))
            loc_row = cursor.fetchone()
            if loc_row:
                resolved_name = loc_row["name"]

        if not resolved_name and not (payload.latitude and payload.longitude):
            resolved_name = "Campus Grounds"

        cursor.execute("""
            INSERT INTO sightings (
                dog_id, location_id, location_name, latitude, longitude, accuracy,
                activity, photo_url, note, submitted_by, source, is_verified, status, ip_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PUBLIC', 1, 'ACTIVE', ?)
        """, (
            dog["id"],
            payload.location_id,
            resolved_name,
            payload.latitude,
            payload.longitude,
            payload.accuracy,
            payload.activity,
            payload.photo_url,
            payload.note,
            payload.submitted_by or "Anonymous Campus Member",
            hashed_ip,
        ))

        sighting_id = cursor.lastrowid

        # Retrieve newly updated last-seen information
        updated_last_seen = resolve_last_seen_for_dog(conn, dog["id"])

        return {
            "status": "SUCCESS",
            "message": f"Thank you for reporting a sighting for {dog['name']}!",
            "sighting_id": sighting_id,
            "dog_uid": clean_uid,
            "dog_name": dog["name"],
            "last_seen": updated_last_seen,
        }

@router.post("/dogs/{dog_uid}/reports", status_code=status.HTTP_201_CREATED, summary="Submit Emergency / Issue Report")
async def submit_dog_report(
    dog_uid: str,
    payload: ReportCreate,
    request: Request,
):
    """
    Public Emergency / Health / Missing Report (Sections 26-27):
    - Report injured dog, sick dog, missing dog, or incorrect info
    - Connects directly to the specific dog being viewed
    - Automatically queued for administrator review and rescue response
    """
    enforce_public_rate_limit(request, endpoint_type="reports")
    clean_uid = dog_uid.strip().upper()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM dogs WHERE dog_uid = ?", (clean_uid,))
        dog = cursor.fetchone()
        if not dog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dog '{clean_uid}' not found.",
            )

        resolved_name = payload.location_name
        if payload.location_id:
            cursor.execute("SELECT name FROM campus_locations WHERE id = ?", (payload.location_id,))
            loc_row = cursor.fetchone()
            if loc_row:
                resolved_name = loc_row["name"]

        cursor.execute("""
            INSERT INTO reports (
                dog_id, report_type, severity, description, location_id, location_name,
                latitude, longitude, photo_url, submitted_by, contact_info, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """, (
            dog["id"],
            payload.report_type,
            payload.severity,
            payload.description,
            payload.location_id,
            resolved_name,
            payload.latitude,
            payload.longitude,
            payload.photo_url,
            payload.submitted_by or "Anonymous Campus Member",
            payload.contact_info,
        ))

        report_id = cursor.lastrowid

        return {
            "status": "SUCCESS",
            "message": f"Emergency report for {dog['name']} has been submitted to campus administrators.",
            "report_id": report_id,
            "dog_uid": clean_uid,
            "report_type": payload.report_type,
            "severity": payload.severity,
        }
