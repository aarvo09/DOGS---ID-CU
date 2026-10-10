from fastapi import APIRouter, Depends
from app.database import get_db
from app.security import get_current_admin
from app.utils import format_time_ago

router = APIRouter(prefix="/api/admin/dashboard", tags=["Admin - Dashboard"])

@router.get("", summary="Get Administrative Dashboard Metrics")
async def get_dashboard_metrics(current_user: dict = Depends(get_current_admin)):
    """
    Returns high-level operational intelligence (Section 33):
    - Total dogs, active dogs, registered tags, recent sightings, open reports
    - Recent sightings stream
    - Pending reports requiring attention
    - At-risk dogs needing attention
    - Recently added dogs
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Operational counters
        cursor.execute("SELECT COUNT(*) as cnt FROM dogs")
        total_dogs = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM dogs WHERE status = 'ACTIVE'")
        active_dogs = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM qr_tags WHERE status = 'ACTIVE'")
        registered_tags = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM qr_tags WHERE status = 'ACTIVE' AND id IN (SELECT tag_id FROM dog_tag_assignments WHERE status = 'ACTIVE')")
        assigned_tags = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM sightings WHERE datetime(created_at) >= datetime('now', '-24 hours')")
        recent_sightings_24h = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM reports WHERE status IN ('PENDING', 'UNDER_REVIEW')")
        open_reports_count = cursor.fetchone()["cnt"]

        # Recent sightings list
        cursor.execute("""
            SELECT s.id, s.created_at, s.activity, s.photo_url, s.source,
                   d.dog_uid, d.name as dog_name,
                   COALESCE(cl.name, s.location_name, 'Campus Grounds') as location_name
            FROM sightings s
            JOIN dogs d ON s.dog_id = d.id
            LEFT JOIN campus_locations cl ON s.location_id = cl.id
            ORDER BY s.created_at DESC, s.id DESC
            LIMIT 10
        """)
        recent_sightings = []
        for r in cursor.fetchall():
            item = dict(r)
            item["time_ago"] = format_time_ago(r["created_at"])
            recent_sightings.append(item)

        # Recent reports list
        cursor.execute("""
            SELECT r.id, r.report_type, r.severity, r.description, r.status, r.created_at,
                   d.dog_uid, d.name as dog_name,
                   COALESCE(cl.name, r.location_name, 'Campus Grounds') as location_name
            FROM reports r
            JOIN dogs d ON r.dog_id = d.id
            LEFT JOIN campus_locations cl ON r.location_id = cl.id
            ORDER BY CASE r.severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, r.created_at DESC
            LIMIT 10
        """)
        recent_reports = []
        for r in cursor.fetchall():
            item = dict(r)
            item["time_ago"] = format_time_ago(r["created_at"])
            recent_reports.append(item)

        # Dogs needing attention
        cursor.execute("""
            SELECT DISTINCT d.id, d.dog_uid, d.name, d.status,
                   h.health_status,
                   (SELECT COUNT(*) FROM reports WHERE dog_id = d.id AND status = 'PENDING') as pending_reports
            FROM dogs d
            LEFT JOIN dog_health_records h ON h.dog_id = d.id
            WHERE d.status = 'MISSING'
               OR h.health_status IN ('NEEDS_ATTENTION', 'CRITICAL', 'UNDER_TREATMENT')
               OR d.id IN (SELECT dog_id FROM reports WHERE status = 'PENDING')
            LIMIT 10
        """)
        dogs_needing_attention = [dict(r) for r in cursor.fetchall()]

        # Recently registered dogs
        cursor.execute("""
            SELECT d.id, d.dog_uid, d.name, d.gender, d.status, d.created_at,
                   t.tag_uid as active_tag_uid
            FROM dogs d
            LEFT JOIN dog_tag_assignments a ON a.dog_id = d.id AND a.status = 'ACTIVE'
            LEFT JOIN qr_tags t ON a.tag_id = t.id AND t.status = 'ACTIVE'
            ORDER BY d.id DESC
            LIMIT 6
        """)
        recently_added_dogs = [dict(r) for r in cursor.fetchall()]

        return {
            "summary": {
                "total_dogs": total_dogs,
                "active_dogs": active_dogs,
                "registered_tags": registered_tags,
                "assigned_tags": assigned_tags,
                "recent_sightings_24h": recent_sightings_24h,
                "open_reports_count": open_reports_count,
            },
            "recent_sightings": recent_sightings,
            "recent_reports": recent_reports,
            "dogs_needing_attention": dogs_needing_attention,
            "recently_added_dogs": recently_added_dogs,
        }
