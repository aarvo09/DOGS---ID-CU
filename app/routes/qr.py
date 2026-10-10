from typing import Optional
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.database import get_db
from app.models import QRResolveResponse

router = APIRouter(tags=["QR Resolution"])

def render_qr_error_html(title: str, message: str, status_code: int, action_button_html: str = "") -> HTMLResponse:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Chandigarh University</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 32px 24px;
            max-width: 420px;
            width: 100%;
            text-align: center;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
            border: 1px solid #e2e8f0;
        }}
        .icon-circle {{
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: #fee2e2;
            color: #dc2626;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            margin: 0 auto 20px auto;
        }}
        .badge {{
            display: inline-block;
            background: #f1f5f9;
            color: #475569;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 9999px;
            margin-bottom: 12px;
        }}
        h1 {{
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 12px 0;
            letter-spacing: -0.5px;
        }}
        p {{
            font-size: 14px;
            line-height: 1.6;
            color: #64748b;
            margin: 0 0 24px 0;
        }}
        .footer-note {{
            font-size: 12px;
            color: #94a3b8;
            border-top: 1px solid #f1f5f9;
            padding-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon-circle">⚠️</div>
        <div class="badge">Chandigarh University Dog Registry</div>
        <h1>{title}</h1>
        <p>{message}</p>
        {action_button_html}
        <div class="footer-note">
            If you found an injured or distressed campus dog, please notify campus security or administration immediately.
        </div>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html, status_code=status_code)

@router.get("/t/{tag_uid}", summary="Resolve Physical QR Tag to Dog Profile")
async def resolve_qr_tag(tag_uid: str, request: Request, format: Optional[str] = None):
    """
    CRITICAL QR RESOLUTION WORKFLOW (Sections 9-13):
    1. Find the QR tag by tag_uid.
    2. Verify that the tag exists -> "QR TAG NOT REGISTERED" (404)
    3. Verify that the tag is active -> "THIS TAG IS CURRENTLY INACTIVE" (403)
    4. Find the current active tag assignment -> "THIS TAG IS NOT CURRENTLY ASSIGNED" (404)
    5. Find the associated dog.
    6. Resolve to the dog profile (/dog/:dogUid).
    
    Rule: A QR scan leads to ONLY the dog associated with that QR tag.
    """
    clean_tag_uid = tag_uid.strip().upper()
    accept_header = request.headers.get("accept", "")
    wants_json = (format == "json") or ("application/json" in accept_header and "text/html" not in accept_header)

    with get_db() as conn:
        cursor = conn.cursor()

        # Step 1: Find QR tag
        cursor.execute("SELECT id, tag_uid, status FROM qr_tags WHERE tag_uid = ?", (clean_tag_uid,))
        tag = cursor.fetchone()

        # Step 2: Verify that the tag exists
        if not tag:
            if wants_json:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "status": "NOT_FOUND",
                        "message": "QR TAG NOT REGISTERED",
                        "tag_uid": clean_tag_uid,
                    }
                )
            return render_qr_error_html(
                title="QR TAG NOT REGISTERED",
                message="This QR code is not recognized by the Chandigarh University Dog Digital Identity System.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Step 3: Verify that the tag is active
        if tag["status"] != "ACTIVE":
            if wants_json:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "status": "INACTIVE",
                        "message": "THIS TAG IS CURRENTLY INACTIVE",
                        "tag_uid": clean_tag_uid,
                    }
                )
            return render_qr_error_html(
                title="THIS TAG IS CURRENTLY INACTIVE",
                message="This QR tag is currently marked as inactive or disabled. No dog information is currently public for this tag.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Step 4 & 5: Find current active tag assignment and associated dog
        cursor.execute("""
            SELECT a.id as assignment_id, a.assigned_at, d.id as dog_id, d.dog_uid, d.name, d.status as dog_status
            FROM dog_tag_assignments a
            JOIN dogs d ON a.dog_id = d.id
            WHERE a.tag_id = ? AND a.status = 'ACTIVE'
            ORDER BY a.assigned_at DESC
            LIMIT 1
        """, (tag["id"],))
        assignment = cursor.fetchone()

        # Unassigned tag check
        if not assignment:
            if wants_json:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "status": "UNASSIGNED",
                        "message": "THIS TAG IS NOT CURRENTLY ASSIGNED",
                        "tag_uid": clean_tag_uid,
                    }
                )
            return render_qr_error_html(
                title="THIS TAG IS NOT CURRENTLY ASSIGNED",
                message=f"Collar Tag ({clean_tag_uid}) is registered in the system but is not currently assigned to any campus dog.",
                status_code=status.HTTP_404_NOT_FOUND,
                action_button_html=f"""
                <div style="margin: 18px 0;">
                    <a href="/admin?tab=tags" style="display: inline-block; background: #c41e3a; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; font-size: 14px;">
                        Staff / Admin? Assign Tag {clean_tag_uid} ➔
                    </a>
                </div>
                """
            )

        # Step 6: Resolve user to dog profile
        dog_uid = assignment["dog_uid"]
        dog_name = assignment["name"]
        redirect_path = f"/dog/{dog_uid}"

        if wants_json:
            return {
                "status": "ASSIGNED",
                "message": "TAG RESOLVED SUCCESSFULLY",
                "tag_uid": clean_tag_uid,
                "dog_uid": dog_uid,
                "dog_name": dog_name,
                "redirect_url": redirect_path,
            }

        # For browser scans, redirect directly to the specific dog profile
        return RedirectResponse(url=redirect_path, status_code=status.HTTP_302_FOUND)
