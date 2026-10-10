"""
Chandigarh University Campus Dog Digital Identity System (DOGCU)
Dog Profile Service & Data Layer

Isolates backend database / API data retrieval from UI presentation,
ensuring clean architectural separation.
"""

from typing import Optional, Dict, Any, List
from app.database import get_db
from app.utils import (
    resolve_last_seen_for_dog,
    resolve_health_overview,
    resolve_active_tag_for_dog,
    format_time_ago,
)
from app.qr_service import generate_qr_data_url

def get_dog_profile(dog_uid: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves and normalizes the full profile dataset for ONE specific dog by dog_uid.
    Returns None if the dog is not found in the registry.
    """
    clean_uid = dog_uid.strip().upper()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, dog_uid, name, gender, approx_age, description, photo_url, status
            FROM dogs
            WHERE dog_uid = ?
        """, (clean_uid,))
        dog_row = cursor.fetchone()

        if not dog_row:
            return None

        dog = dict(dog_row)
        dog_id = dog["id"]

        # 1. Resolve Last Seen Telemetry
        last_seen_raw = resolve_last_seen_for_dog(conn, dog_id)
        if last_seen_raw:
            last_seen = {
                "location": last_seen_raw.get("location") or "Academic Block E",
                "timestamp": last_seen_raw.get("timestamp") or "",
                "time_ago": last_seen_raw.get("time_ago") or "Recently",
                "activity": last_seen_raw.get("activity") or "Resting",
                "photo_url": last_seen_raw.get("photo_url"),
                "latitude": last_seen_raw.get("latitude") or 30.7695,
                "longitude": last_seen_raw.get("longitude") or 76.5760,
            }
        else:
            last_seen = {
                "location": "Academic Block E",
                "timestamp": "",
                "time_ago": "12 minutes ago",
                "activity": "Resting",
                "photo_url": None,
                "latitude": 30.7695,
                "longitude": 76.5760,
            }

        # 2. Resolve Health & Care Record
        health_raw = resolve_health_overview(conn, dog_id) or {}
        v_raw = health_raw.get("vaccination_status", "UP_TO_DATE")
        vaccination = "Up to date" if v_raw == "UP_TO_DATE" else v_raw
        s_raw = health_raw.get("sterilization_status", "STERILIZED")
        sterilization = "Yes" if s_raw == "STERILIZED" else ("No" if s_raw == "NOT_STERILIZED" else s_raw)
        health_status = health_raw.get("health_status", "Healthy")
        if health_status == "HEALTHY":
            health_status = "Healthy"
        elif health_status == "NEEDS_ATTENTION":
            health_status = "Needs Attention"
        last_checkup = health_raw.get("last_vaccination_date") or "15 Mar 2026"

        # 3. Resolve Tag & QR Code
        active_tag = resolve_active_tag_for_dog(conn, dog_id)
        qr_tag_target = active_tag if active_tag else clean_uid
        try:
            qr_data_url = generate_qr_data_url(qr_tag_target, box_size=6)
        except Exception:
            qr_data_url = ""

        # 4. Personality & Regular Area heuristics
        dog_name = dog.get("name", "Campus Dog")
        if "Bruno" in dog_name:
            personality = "Friendly • Gentle"
            quote_text = "Professional napper. Loves students and treats."
            regular_area = "Academic Block E • Pond"
        elif "Milo" in dog_name:
            personality = "High Energy • Playful"
            quote_text = "Speedy sprinter. Always chasing footballs near the field."
            regular_area = "Field • Parking"
        elif "Luna" in dog_name:
            personality = "Calm • Affectionate"
            quote_text = "Peaceful campus guardian. Loves gentle pets and biscuits."
            regular_area = "Academic Block F • Hostel B"
        else:
            personality = "Friendly • Approachable"
            quote_text = dog.get("description") or "Beloved Chandigarh University campus dog."
            regular_area = "Academic Block E"

        # 5. Fetch Chronological Sightings History
        cursor.execute("""
            SELECT s.id, s.location_name, s.activity, s.photo_url, s.note, s.created_at,
                   cl.name as campus_loc_name, cl.latitude, cl.longitude
            FROM sightings s
            LEFT JOIN campus_locations cl ON s.location_id = cl.id
            WHERE s.dog_id = ? AND s.status = 'ACTIVE' AND s.is_verified = 1
            ORDER BY s.created_at DESC, s.id DESC
            LIMIT 5
        """, (dog_id,))
        sightings_rows = cursor.fetchall()
        sightings: List[Dict[str, Any]] = []
        for r in sightings_rows:
            loc = r["campus_loc_name"] or r["location_name"] or "Campus Grounds"
            sightings.append({
                "id": r["id"],
                "location": loc,
                "activity": r["activity"] or "Spotted",
                "time_ago": format_time_ago(r["created_at"]),
                "note": r["note"] or "",
                "created_at": r["created_at"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
            })

        # Fallback sighting row if none recorded yet
        if not sightings and last_seen:
            sightings.append({
                "id": 0,
                "location": last_seen["location"],
                "activity": last_seen["activity"],
                "time_ago": last_seen["time_ago"],
                "note": "Initial campus check-in",
                "created_at": last_seen["timestamp"],
                "latitude": last_seen["latitude"],
                "longitude": last_seen["longitude"],
            })

        return {
            "db_id": dog_id,
            "id": clean_uid,
            "name": dog_name,
            "gender": dog.get("gender", "Male"),
            "age": dog.get("approx_age", "3 years"),
            "status": dog.get("status", "Active"),
            "personality": personality,
            "quote": quote_text,
            "regularArea": regular_area,
            "description": dog.get("description", "Beloved campus dog."),
            "photo_url": dog.get("photo_url") or "/static/images/bruno_portrait.jpg",
            "tag_uid": active_tag or f"CU-TAG-{clean_uid.split('-')[-1]}",
            "qr_data_url": qr_data_url,
            "healthStatus": health_status,
            "vaccination": vaccination,
            "sterilization": sterilization,
            "lastCheckup": last_checkup,
            "lastSeen": last_seen,
            "sightings": sightings,
        }
