from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.database import get_db
from app.models import ReportUpdate
from app.security import get_current_admin, require_roles
from app.utils import format_time_ago

router = APIRouter(prefix="/api/admin/reports", tags=["Admin - Reports"])

@router.get("", summary="List Campus Dog Reports (Admin)")
async def list_admin_reports(
    status_filter: Optional[str] = None,
    report_type: Optional[str] = None,
    severity: Optional[str] = None,
    dog_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT r.*, d.dog_uid, d.name as dog_name, cl.name as campus_loc_name,
                   u.name as resolved_by_name
            FROM reports r
            JOIN dogs d ON r.dog_id = d.id
            LEFT JOIN campus_locations cl ON r.location_id = cl.id
            LEFT JOIN admin_users u ON r.resolved_by = u.id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND r.status = ?"
            params.append(status_filter)
        if report_type:
            query += " AND r.report_type = ?"
            params.append(report_type)
        if severity:
            query += " AND r.severity = ?"
            params.append(severity)
        if dog_id:
            query += " AND r.dog_id = ?"
            params.append(dog_id)

        query += " ORDER BY CASE r.severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, r.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            item = dict(r)
            item["resolved_location"] = r["campus_loc_name"] or r["location_name"] or "Campus Grounds"
            item["time_ago"] = format_time_ago(r["created_at"])
            results.append(item)

        return {
            "limit": limit,
            "offset": offset,
            "reports": results,
        }

@router.get("/{report_id}", summary="Get Report Details (Admin)")
async def get_report_detail(
    report_id: int,
    current_user: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, d.dog_uid, d.name as dog_name, cl.name as campus_loc_name,
                   u.name as resolved_by_name
            FROM reports r
            JOIN dogs d ON r.dog_id = d.id
            LEFT JOIN campus_locations cl ON r.location_id = cl.id
            LEFT JOIN admin_users u ON r.resolved_by = u.id
            WHERE r.id = ?
        """, (report_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

        item = dict(row)
        item["resolved_location"] = row["campus_loc_name"] or row["location_name"] or "Campus Grounds"
        item["time_ago"] = format_time_ago(row["created_at"])
        return item

@router.patch("/{report_id}", summary="Update / Resolve Report (Admin)")
async def update_report(
    report_id: int,
    payload: ReportUpdate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN", "ADMIN"])),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        report = cursor.fetchone()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

        fields = []
        values = []
        if payload.status is not None:
            fields.append("status = ?")
            values.append(payload.status)
            if payload.status == "RESOLVED":
                fields.append("resolved_by = ?")
                values.append(current_user["id"])
                fields.append("resolved_at = CURRENT_TIMESTAMP")
        if payload.admin_notes is not None:
            fields.append("admin_notes = ?")
            values.append(payload.admin_notes)

        if fields:
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(report_id)
            cursor.execute(f"UPDATE reports SET {', '.join(fields)} WHERE id = ?", values)

        cursor.execute("""
            SELECT r.*, d.dog_uid, d.name as dog_name, u.name as resolved_by_name
            FROM reports r
            JOIN dogs d ON r.dog_id = d.id
            LEFT JOIN admin_users u ON r.resolved_by = u.id
            WHERE r.id = ?
        """, (report_id,))
        return dict(cursor.fetchone())
