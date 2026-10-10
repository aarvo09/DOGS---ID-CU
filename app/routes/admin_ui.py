"""
Chandigarh University Campus Dog Digital Identity System (DOGCU)
Admin Web Portal Routes: Authentication, Dashboard, and Interactive Dog Management
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from app.database import get_db
from app.security import (
    authenticate_user,
    create_access_token,
    get_optional_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.admin_views import render_admin_login_page, render_admin_dashboard_page
from app.id_generator import generate_dog_uid, generate_tag_uid
from app.utils import format_time_ago, resolve_last_seen_for_dog
from app.qr_service import (
    generate_printable_a4_sheet_html,
    generate_printable_a4_sheet_pdf,
    generate_printable_a4_sheet_png,
)

router = APIRouter(include_in_schema=False)

COOKIE_NAME = "dogcu_access_token"

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_view(request: Request, next: str = "/admin", error: Optional[str] = None):
    """Renders the admin login page or redirects if already authenticated."""
    admin = get_optional_admin(request)
    if admin:
        return RedirectResponse(url=next or "/admin", status_code=status.HTTP_303_SEE_OTHER)
    return HTMLResponse(content=render_admin_login_page(next_url=next, error_msg=error))


@router.post("/admin/login")
async def admin_login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/admin"),
):
    """Processes admin credentials, issues JWT token in HTTP cookie, and redirects."""
    user = authenticate_user(email.strip(), password)
    if not user:
        return HTMLResponse(
            content=render_admin_login_page(
                next_url=next,
                error_msg="Invalid credentials. Please verify your email and password."
            ),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Issue token
    token = create_access_token(data={
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
        "name": user["name"],
    })

    redirect_target = next if next and next.startswith("/") else "/admin"
    response = RedirectResponse(url=redirect_target, status_code=status.HTTP_303_SEE_OTHER)
    
    # Set persistent cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return response


@router.get("/admin/logout")
async def admin_logout_view(next: str = "/admin/login"):
    """Clears authentication cookie and redirects to login."""
    target = next if next and next.startswith("/") else "/admin/login"
    response = RedirectResponse(url=target, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return response


@router.get("/admin", response_class=HTMLResponse)
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_view(
    request: Request,
    tab: str = "dogs",
    msg: Optional[str] = None,
):
    """
    Renders the unified Chandigarh University Campus Dog Administrative Dashboard.
    Requires authenticated session (via cookie or header).
    """
    admin = get_optional_admin(request)
    if not admin:
        return RedirectResponse(url=f"/admin/login?next={request.url.path}", status_code=status.HTTP_303_SEE_OTHER)

    with get_db() as conn:
        cursor = conn.cursor()

        # Operational metrics
        cursor.execute("SELECT COUNT(*) as cnt FROM dogs")
        total_dogs = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM dogs WHERE status = 'ACTIVE'")
        active_dogs = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM qr_tags WHERE status = 'ACTIVE'")
        total_tags = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM qr_tags WHERE status = 'ACTIVE' AND id IN (SELECT tag_id FROM dog_tag_assignments WHERE status = 'ACTIVE')")
        assigned_tags = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM sightings")
        total_sightings = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM reports WHERE status IN ('PENDING', 'UNDER_REVIEW')")
        pending_reports = cursor.fetchone()["cnt"]

        metrics = {
            "dogs": {"total": total_dogs, "active": active_dogs},
            "tags": {"total": total_tags, "assigned": assigned_tags},
            "sightings": {"total": total_sightings},
            "reports": {"pending": pending_reports},
        }

        # Dogs list
        cursor.execute("""
            SELECT d.*, 
                   t.tag_uid as active_tag_uid,
                   (SELECT COUNT(*) FROM sightings WHERE dog_id = d.id) as sightings_count,
                   (SELECT COUNT(*) FROM reports WHERE dog_id = d.id AND status = 'PENDING') as open_reports_count,
                   (SELECT health_status FROM dog_health_records WHERE dog_id = d.id ORDER BY id DESC LIMIT 1) as health_status
            FROM dogs d
            LEFT JOIN dog_tag_assignments a ON a.dog_id = d.id AND a.status = 'ACTIVE'
            LEFT JOIN qr_tags t ON a.tag_id = t.id AND t.status = 'ACTIVE'
            ORDER BY d.id DESC
        """)
        dogs_raw = cursor.fetchall()
        dogs = []
        for r in dogs_raw:
            dog_dict = dict(r)
            dog_dict["last_seen"] = resolve_last_seen_for_dog(conn, r["id"])
            dogs.append(dog_dict)

        # Physical QR tags
        cursor.execute("""
            SELECT t.id, t.tag_uid, t.status, t.created_at,
                   d.dog_uid as assigned_dog_uid, d.name as assigned_dog_name, d.id as assigned_dog_id,
                   a.assigned_at
            FROM qr_tags t
            LEFT JOIN dog_tag_assignments a ON a.tag_id = t.id AND a.status = 'ACTIVE'
            LEFT JOIN dogs d ON a.dog_id = d.id
            ORDER BY t.id DESC
        """)
        tags = [dict(r) for r in cursor.fetchall()]

        # Recent Sightings
        cursor.execute("""
            SELECT s.id, s.created_at, s.activity, s.photo_url, s.source, s.note, s.submitted_by,
                   d.dog_uid, d.name as dog_name,
                   COALESCE(cl.name, s.location_name, 'Campus Grounds') as location_name
            FROM sightings s
            JOIN dogs d ON s.dog_id = d.id
            LEFT JOIN campus_locations cl ON s.location_id = cl.id
            ORDER BY s.created_at DESC, s.id DESC
            LIMIT 50
        """)
        sightings_raw = cursor.fetchall()
        sightings = []
        for r in sightings_raw:
            item = dict(r)
            item["time_ago"] = format_time_ago(r["created_at"])
            sightings.append(item)

        # Emergency & Community Reports
        cursor.execute("""
            SELECT r.id, r.report_type, r.severity, r.description, r.status, r.created_at, r.contact_info,
                   d.dog_uid, d.name as dog_name,
                   COALESCE(cl.name, r.location_name, 'Campus Grounds') as location_name,
                   u.name as resolved_by_name
            FROM reports r
            JOIN dogs d ON r.dog_id = d.id
            LEFT JOIN campus_locations cl ON r.location_id = cl.id
            LEFT JOIN admin_users u ON r.resolved_by = u.id
            ORDER BY CASE r.severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, r.created_at DESC
            LIMIT 50
        """)
        reports_raw = cursor.fetchall()
        reports = []
        for r in reports_raw:
            item = dict(r)
            item["time_ago"] = format_time_ago(r["created_at"])
            reports.append(item)

        # Campus Locations
        cursor.execute("""
            SELECT cl.*,
                   (SELECT COUNT(*) FROM sightings WHERE location_id = cl.id) as sightings_count
            FROM campus_locations cl
            ORDER BY cl.name ASC
        """)
        locations = [dict(r) for r in cursor.fetchall()]

    html_content = render_admin_dashboard_page(
        current_user=admin,
        metrics=metrics,
        dogs=dogs,
        tags=tags,
        sightings=sightings,
        reports=reports,
        locations=locations,
        active_tab=tab,
        message=msg,
    )
    return HTMLResponse(content=html_content)


@router.post("/admin/dogs/create")
async def admin_create_dog_post(
    request: Request,
    name: str = Form(...),
    gender: str = Form("Male"),
    approx_age: str = Form("2 years"),
    description: Optional[str] = Form(None),
    photo_url: Optional[str] = Form(None),
    status_val: str = Form("ACTIVE"),
    dog_uid_custom: Optional[str] = Form(None),
    assign_tag_id: Optional[int] = Form(None),
    health_status: str = Form("HEALTHY"),
    vaccination_status: str = Form("UP_TO_DATE"),
    sterilization_status: str = Form("YES"),
):
    """Registers a new campus dog from the admin dashboard form."""
    admin = get_optional_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    with get_db() as conn:
        cursor = conn.cursor()

        # Generate or clean Dog UID
        if dog_uid_custom and dog_uid_custom.strip():
            dog_uid = dog_uid_custom.strip().upper()
        else:
            dog_uid = generate_dog_uid(conn)

        # Insert Dog
        cursor.execute("""
            INSERT INTO dogs (dog_uid, name, gender, approx_age, description, photo_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dog_uid,
            name.strip(),
            gender,
            approx_age.strip(),
            description.strip() if description else None,
            photo_url.strip() if photo_url else "/static/images/bruno_portrait.jpg",
            status_val,
        ))
        new_dog_id = cursor.lastrowid

        # Insert initial health record
        cursor.execute("""
            INSERT INTO dog_health_records (
                dog_id, vaccination_status, sterilization_status, health_status, notes, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            new_dog_id,
            vaccination_status,
            sterilization_status,
            health_status,
            "Initial registration health profile",
            admin.get("id"),
        ))

        # Optional tag assignment
        if assign_tag_id:
            cursor.execute("SELECT id FROM qr_tags WHERE id = ? AND status = 'ACTIVE'", (assign_tag_id,))
            if cursor.fetchone():
                cursor.execute("""
                    INSERT INTO dog_tag_assignments (dog_id, tag_id, assigned_by, status)
                    VALUES (?, ?, ?, 'ACTIVE')
                """, (new_dog_id, assign_tag_id, admin.get("id")))

    return RedirectResponse(
        url=f"/admin?tab=dogs&msg=Registered+{name.strip()}+({dog_uid})+successfully!",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/dogs/{dog_id}/update")
async def admin_update_dog_post(
    request: Request,
    dog_id: int,
    name: str = Form(...),
    gender: str = Form(...),
    approx_age: str = Form(...),
    description: Optional[str] = Form(None),
    photo_url: Optional[str] = Form(None),
    status_val: str = Form("ACTIVE"),
    health_status: Optional[str] = Form(None),
    vaccination_status: Optional[str] = Form(None),
    sterilization_status: Optional[str] = Form(None),
    health_notes: Optional[str] = Form(None),
    next_url: Optional[str] = Form(None),
):
    """
    Updates official dog profile and health records.
    Supports seamless redirect back to the dog's public profile or the admin panel.
    """
    admin = get_optional_admin(request)
    if not admin:
        return RedirectResponse(url=f"/admin/login?next={next_url or '/admin'}", status_code=status.HTTP_303_SEE_OTHER)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, dog_uid, name FROM dogs WHERE id = ?", (dog_id,))
        dog = cursor.fetchone()
        if not dog:
            return RedirectResponse(url="/admin?msg=Dog+not+found", status_code=status.HTTP_303_SEE_OTHER)

        # Update core dog master data
        cursor.execute("""
            UPDATE dogs 
            SET name = ?, gender = ?, approx_age = ?, description = ?, photo_url = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            name.strip(),
            gender,
            approx_age.strip(),
            description.strip() if description else None,
            photo_url.strip() if photo_url else None,
            status_val,
            dog_id,
        ))

        # Add updated health record if health fields were modified
        if health_status or vaccination_status or sterilization_status:
            cursor.execute("""
                INSERT INTO dog_health_records (
                    dog_id, vaccination_status, sterilization_status, health_status, notes, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                dog_id,
                vaccination_status or "UP_TO_DATE",
                sterilization_status or "YES",
                health_status or "HEALTHY",
                health_notes.strip() if health_notes else f"Updated by {admin.get('name', 'Admin')}",
                admin.get("id"),
            ))

    redirect_target = next_url if next_url and next_url.startswith("/") else "/admin?tab=dogs"
    delimiter = "&" if "?" in redirect_target else "?"
    return RedirectResponse(
        url=f"{redirect_target}{delimiter}msg=Updated+{name.strip()}+profile+successfully!",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/tags/create")
async def admin_create_tag_post(
    request: Request,
    batch_count: int = Form(1),
):
    """Generates new official QR collar tags."""
    admin = get_optional_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    count = max(1, min(batch_count, 10))
    generated_tags = []
    with get_db() as conn:
        cursor = conn.cursor()
        for _ in range(count):
            tag_uid = generate_tag_uid(conn)
            cursor.execute("INSERT INTO qr_tags (tag_uid, status) VALUES (?, 'ACTIVE')", (tag_uid,))
            generated_tags.append(tag_uid)

    return RedirectResponse(
        url=f"/admin?tab=tags&msg=Generated+{count}+new+collar+tag(s):+{', '.join(generated_tags)}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/tags/assign")
async def admin_assign_tag_post(
    request: Request,
    tag_id: int = Form(...),
    dog_id: int = Form(...),
):
    """Assigns an unassigned collar tag to a campus dog."""
    admin = get_optional_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    with get_db() as conn:
        cursor = conn.cursor()
        # Retire any prior active assignment for this dog
        cursor.execute("""
            UPDATE dog_tag_assignments 
            SET status = 'REPLACED', unassigned_at = CURRENT_TIMESTAMP
            WHERE dog_id = ? AND status = 'ACTIVE'
        """, (dog_id,))

        # Retire any prior active assignment for this tag
        cursor.execute("""
            UPDATE dog_tag_assignments 
            SET status = 'REPLACED', unassigned_at = CURRENT_TIMESTAMP
            WHERE tag_id = ? AND status = 'ACTIVE'
        """, (tag_id,))

        # Create new assignment
        cursor.execute("""
            INSERT INTO dog_tag_assignments (dog_id, tag_id, assigned_by, status)
            VALUES (?, ?, ?, 'ACTIVE')
        """, (dog_id, tag_id, admin.get("id")))

    return RedirectResponse(
        url="/admin?tab=tags&msg=Collar+tag+successfully+assigned!",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/reports/{report_id}/status")
async def admin_update_report_status_post(
    request: Request,
    report_id: int,
    status_val: str = Form(...),
    resolution_notes: Optional[str] = Form(None),
):
    """Updates the status of an emergency or animal welfare report."""
    admin = get_optional_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    with get_db() as conn:
        cursor = conn.cursor()
        resolved_at = datetime.now(timezone.utc).isoformat() if status_val in ("RESOLVED", "DISMISSED") else None
        resolved_by = admin.get("id") if status_val in ("RESOLVED", "DISMISSED") else None

        cursor.execute("""
            UPDATE reports 
            SET status = ?, resolution_notes = ?, resolved_at = ?, resolved_by = ?
            WHERE id = ?
        """, (
            status_val,
            resolution_notes.strip() if resolution_notes else None,
            resolved_at,
            resolved_by,
            report_id,
        ))

    return RedirectResponse(
        url=f"/admin?tab=reports&msg=Report+marked+as+{status_val}!",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/admin/tags/print/a4-sheet", response_class=HTMLResponse)
@router.get("/admin/tags/print-sheet", response_class=HTMLResponse)
@router.get("/print/qr-sheet", response_class=HTMLResponse)
@router.get("/print/a4", response_class=HTMLResponse)
async def print_a4_collar_tags_sheet_view(request: Request, base_url: Optional[str] = None):
    """
    Renders the official A4 Printable Sheet containing 10 static QR collar tags (2cm x 2cm).
    Formatted strictly for standard A4 paper with 'SCAN ME' and custom colorful QR codes.
    Optionally accepts ?base_url=https://your-domain.com to bake a live domain into the QRs.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.tag_uid, t.status,
                   d.dog_uid, d.name as dog_name
            FROM qr_tags t
            LEFT JOIN dog_tag_assignments a ON a.tag_id = t.id AND a.status = 'ACTIVE'
            LEFT JOIN dogs d ON a.dog_id = d.id
            WHERE t.status = 'ACTIVE'
            ORDER BY t.id ASC
            LIMIT 10
        """)
        tags = [dict(r) for r in cursor.fetchall()]

    return HTMLResponse(content=generate_printable_a4_sheet_html(tags, base_url=base_url))


@router.get("/print/robox-collar-tags.pdf")
@router.get("/print/download-pdf")
async def download_a4_collar_tags_pdf(request: Request, base_url: Optional[str] = None):
    """
    Directly generates and streams an authentic, print-ready A4 PDF document containing
    10 static dog collar tags with 2cm x 2cm QR code, 'SCAN ME', and 'ROBO X'.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.tag_uid, t.status
            FROM qr_tags t
            WHERE t.status = 'ACTIVE'
            ORDER BY t.id ASC
            LIMIT 10
        """)
        tags = [dict(r) for r in cursor.fetchall()]

    pdf_bytes = generate_printable_a4_sheet_pdf(tags, base_url=base_url)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="robox-collar-tags-a4.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        }
    )


@router.get("/print/robox-collar-tags.png")
@router.get("/print/download-png")
async def download_a4_collar_tags_png(request: Request, base_url: Optional[str] = None):
    """
    Directly generates and streams an authentic high-resolution 300 DPI A4 PNG image (2480 x 3508 px)
    containing 10 static dog collar tags with 2cm x 2cm QR code, 'SCAN ME', and 'ROBO X'.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.tag_uid, t.status
            FROM qr_tags t
            WHERE t.status = 'ACTIVE'
            ORDER BY t.id ASC
            LIMIT 10
        """)
        tags = [dict(r) for r in cursor.fetchall()]

    png_bytes = generate_printable_a4_sheet_png(tags, base_url=base_url)
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": 'attachment; filename="robox-collar-tags-a4.png"',
            "Content-Length": str(len(png_bytes)),
        }
    )


