import hashlib
from datetime import datetime, timezone
from typing import Optional
import sqlite3

def hash_client_ip(ip: Optional[str]) -> str:
    """Hash client IP with a fixed salt to protect user privacy while enabling rate-limiting."""
    if not ip:
        return "unknown"
    return hashlib.sha256(f"dogcu-salt-{ip}".encode("utf-8")).hexdigest()[:16]

def parse_iso_datetime(dt_val: Optional[str]) -> Optional[datetime]:
    if not dt_val:
        return None
    try:
        # SQLite CURRENT_TIMESTAMP is "YYYY-MM-DD HH:MM:SS" (UTC)
        if "T" in dt_val:
            return datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
        else:
            return datetime.strptime(dt_val, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None

def format_time_ago(dt_val: Optional[str]) -> str:
    """Format an SQLite timestamp into a friendly human-readable relative time."""
    parsed = parse_iso_datetime(dt_val)
    if not parsed:
        return "Recently"

    now = datetime.now(timezone.utc)
    diff = now - parsed
    seconds = int(diff.total_seconds())

    if seconds < 0:
        return "Just now"
    if seconds < 60:
        return "Just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''} ago"
    weeks = days // 7
    if weeks < 4:
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"

def resolve_last_seen_for_dog(conn: sqlite3.Connection, dog_id: int) -> Optional[dict]:
    """
    Determine the dog's latest valid sighting.
    This resolves the public 'Last Spotted' information dynamically
    from the newest active and non-flagged sighting.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.location_name, s.activity, s.photo_url, s.created_at,
               cl.name as campus_loc_name, cl.latitude, cl.longitude
        FROM sightings s
        LEFT JOIN campus_locations cl ON s.location_id = cl.id
        WHERE s.dog_id = ? AND s.status = 'ACTIVE' AND s.is_verified = 1
        ORDER BY s.created_at DESC, s.id DESC
        LIMIT 1
    """, (dog_id,))
    row = cursor.fetchone()
    if not row:
        return None

    resolved_location = row["campus_loc_name"] or row["location_name"] or "Campus Grounds"
    return {
        "location": resolved_location,
        "timestamp": row["created_at"],
        "time_ago": format_time_ago(row["created_at"]),
        "activity": row["activity"],
        "photo_url": row["photo_url"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
    }

def resolve_health_overview(conn: sqlite3.Connection, dog_id: int) -> Optional[dict]:
    """Retrieve the official health status and summary for a dog."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vaccination_status, last_vaccination_date, sterilization_status, health_status
        FROM dog_health_records
        WHERE dog_id = ?
        ORDER BY updated_at DESC, id DESC
        LIMIT 1
    """, (dog_id,))
    row = cursor.fetchone()
    if not row:
        return {
            "vaccination_status": "UNKNOWN",
            "last_vaccination_date": None,
            "sterilization_status": "UNKNOWN",
            "health_status": "HEALTHY",
        }
    return {
        "vaccination_status": row["vaccination_status"],
        "last_vaccination_date": row["last_vaccination_date"],
        "sterilization_status": row["sterilization_status"],
        "health_status": row["health_status"],
    }

def resolve_active_tag_for_dog(conn: sqlite3.Connection, dog_id: int) -> Optional[str]:
    """Find the current active tag_uid assigned to the dog, if any."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.tag_uid
        FROM dog_tag_assignments a
        JOIN qr_tags t ON a.tag_id = t.id
        WHERE a.dog_id = ? AND a.status = 'ACTIVE' AND t.status = 'ACTIVE'
        LIMIT 1
    """, (dog_id,))
    row = cursor.fetchone()
    return row["tag_uid"] if row else None
