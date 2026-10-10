"""
Chandigarh University Campus Dog Digital Identity System (DOGCU)
Admin Portal Views: Login & Comprehensive Management Dashboard
"""

import html
from typing import Dict, Any, List, Optional

def p_emoji(name: str, alt: str = "", size: str = "", extra_class: str = "") -> str:
    """Renders authentic hand-drawn field notebook doodle emoji."""
    size_cls = f" premium-emoji--{size}" if size else ""
    extra = f" {extra_class}" if extra_class else ""
    return f'<img src="/static/assets/emojis/{name}.webp" class="premium-emoji{size_cls}{extra}" alt="{alt}" draggable="false" />'

def render_admin_login_page(next_url: str = "/admin", error_msg: Optional[str] = None) -> str:
    """Renders the administrative authentication screen."""
    clean_next = html.escape(next_url)
    back_target = clean_next if (clean_next and clean_next.startswith("/dog/")) else "/dog/CU-DOG-024"
    error_html = f"""
    <div class="alert-box error">
        <span>{p_emoji('warning', 'Warning')}</span>
        <div>{html.escape(error_msg)}</div>
    </div>
    """ if error_msg else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Portal — RoboX Club • Chandigarh University</title>
    <style>
        .premium-emoji {{
            display: inline-block;
            vertical-align: -0.2em;
            width: 1.25em;
            height: 1.25em;
            object-fit: contain;
            pointer-events: none;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.15));
        }}
        .premium-emoji--sm {{ width: 1.05em; height: 1.05em; }}
        .premium-emoji--md {{ width: 1.35em; height: 1.35em; }}
        .premium-emoji--lg {{ width: 1.75em; height: 1.75em; }}
        :root {{
            --cu-red: #c41e3a;
            --cu-red-dark: #991b1b;
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --border-color: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px 16px;
        }}
        .login-nav-header {{
            width: 100%;
            max-width: 440px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .login-nav-back-button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #1e293b;
            color: #f8fafc;
            border: 1.5px solid #475569;
            border-radius: 10px;
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .login-nav-back-button:hover {{
            background: #334155;
            border-color: #ef4444;
            transform: translateX(-2px);
        }}
        .login-nav-badge {{
            font-size: 12px;
            font-weight: 700;
            color: #94a3b8;
            letter-spacing: 0.5px;
        }}
        .login-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            max-width: 440px;
            width: 100%;
            padding: 36px 32px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .brand-header {{
            text-align: center;
            margin-bottom: 28px;
        }}
        .cu-badge {{
            display: inline-block;
            background: #dc2626;
            color: white;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            padding: 5px 14px;
            border-radius: 9999px;
            margin-bottom: 14px;
        }}
        .brand-title {{
            font-size: 24px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }}
        .brand-subtitle {{
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.4;
        }}
        .alert-box {{
            background: #450a0a;
            border: 1px solid #dc2626;
            color: #fecaca;
            border-radius: 10px;
            padding: 12px 14px;
            font-size: 13px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .form-group {{
            margin-bottom: 18px;
        }}
        label {{
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 6px;
        }}
        input[type="email"], input[type="password"] {{
            width: 100%;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 12px 14px;
            color: white;
            font-size: 15px;
            outline: none;
            transition: all 0.2s ease;
        }}
        input:focus {{
            border-color: #ef4444;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
        }}
        .btn-submit {{
            width: 100%;
            background: #dc2626;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 13px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 8px;
        }}
        .btn-submit:hover {{
            background: #b91c1c;
            transform: translateY(-1px);
        }}
        .back-link {{
            display: block;
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: #64748b;
            text-decoration: none;
        }}
        .back-link:hover {{
            color: #cbd5e1;
        }}
    </style>
</head>
<body>
    <header class="login-nav-header">
        <a href="{back_target}" class="login-nav-back-button" id="login-back-btn">
            <span>←</span>
            <span>Back to Dog Profile</span>
        </a>
        <div class="login-nav-badge">
            <span>🐾 CU Campus Dogs</span>
        </div>
    </header>

    <div class="login-card">
        <div class="brand-header">
            <span class="cu-badge">Admin Portal</span>
            <h1 class="brand-title">RoboX Club</h1>
            <p class="brand-subtitle">Chandigarh University Campus Dogs Admin System</p>
        </div>

        {error_html}

        <form method="POST" action="/admin/login" id="login-form">
            <input type="hidden" name="next_url" value="{clean_next}">

            <div class="form-group">
                <label for="email">Admin Email Address</label>
                <input type="email" id="email" name="email" required autocomplete="email" placeholder="admin@cumail.in">
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password" placeholder="••••••••">
            </div>

            <button type="submit" class="btn-submit">Sign In to Admin Portal ➔</button>
        </form>

        <a href="{back_target}" class="back-link">← Return to Field Notebook</a>
    </div>
</body>
</html>
"""


def render_admin_dashboard_page(
    current_user: Dict[str, Any],
    metrics: Dict[str, Any],
    dogs: List[Dict[str, Any]],
    tags: List[Dict[str, Any]],
    sightings: List[Dict[str, Any]],
    reports: List[Dict[str, Any]],
    locations: List[Dict[str, Any]],
    active_tab: str = "dogs",
    message: Optional[str] = None,
) -> str:
    """Renders the comprehensive administrative dashboard."""
    user_name = html.escape(current_user.get("name", "Administrator"))
    user_role = html.escape(current_user.get("role", "ADMIN"))
    clean_msg = f'<div class="flash-toast">{html.escape(message)}</div>' if message else ""

    total_dogs = metrics.get("dogs", {}).get("total", len(dogs))
    active_dogs = metrics.get("dogs", {}).get("active", len(dogs))
    total_tags = metrics.get("tags", {}).get("total", len(tags))
    assigned_tags = metrics.get("tags", {}).get("assigned", 0)
    total_sightings = metrics.get("sightings", {}).get("total", len(sightings))
    pending_reports = metrics.get("reports", {}).get("pending", 0)

    # Generate Dog Rows
    dog_rows_html = ""
    for d in dogs:
        d_id = d["id"]
        d_uid = html.escape(d["dog_uid"])
        d_name = html.escape(d["name"])
        d_gender = html.escape(d["gender"])
        d_age = html.escape(d["approx_age"])
        d_status = html.escape(d.get("status", "ACTIVE"))
        d_photo = html.escape(d.get("photo_url") or "/static/images/bruno_portrait.jpg")
        d_tag = html.escape(d.get("active_tag_uid") or "None")
        d_health = html.escape(d.get("health_status") or "Healthy")
        d_desc = html.escape(d.get("description") or "")
        
        status_badge_class = "badge-green" if d_status == "ACTIVE" else "badge-yellow"

        dog_rows_html += f"""
        <tr class="data-row">
            <td style="width: 50px;">
                <img src="{d_photo}" alt="{d_name}" class="dog-thumb" onerror="this.src='/static/assets/dogs/bruno.png'">
            </td>
            <td>
                <strong>{d_name}</strong>
                <div style="font-size: 11px; color: #64748b; font-family: monospace;">{d_uid}</div>
            </td>
            <td>
                <span class="tag-pill">{d_tag}</span>
            </td>
            <td>{d_gender} • {d_age}</td>
            <td>
                <span class="health-pill">{d_health}</span>
            </td>
            <td>
                <span class="status-badge {status_badge_class}">{d_status}</span>
            </td>
            <td style="text-align: right;">
                <a href="/dog/{d_uid}" class="btn-sm btn-outline" target="_blank" title="View Public Field Notebook">{p_emoji('eye', 'View')} View</a>
                <button type="button" class="btn-sm btn-primary" onclick="openEditDogModal({d_id}, '{d_name}', '{d_uid}', '{d_gender}', '{d_age}', '{d_status}', '{d_photo}', '{d_desc}')">{p_emoji('pencil', 'Edit')} Edit</button>
            </td>
        </tr>
        """

    # Generate Tag Rows
    tag_rows_html = ""
    for t in tags:
        t_id = t["id"]
        t_uid = html.escape(t["tag_uid"])
        t_status = html.escape(t["status"])
        t_assigned_dog = html.escape(t.get("dog_name") or t.get("dog_uid") or "Unassigned")
        t_assigned = t.get("dog_id") is not None
        badge_cls = "badge-green" if t_status == "ACTIVE" else "badge-red"

        tag_rows_html += f"""
        <tr class="data-row">
            <td>
                <span class="tag-pill" style="font-size: 13px;">{t_uid}</span>
            </td>
            <td>
                <span class="status-badge {badge_cls}">{t_status}</span>
            </td>
            <td>
                {t_assigned_dog if t_assigned else '<em style="color: #64748b;">Ready to assign</em>'}
            </td>
            <td style="text-align: right;">
                <a href="/api/admin/tags/{t_id}/printable-badge" target="_blank" class="btn-sm btn-outline">{p_emoji('printer', 'Print')} Print Badge</a>
                <a href="/t/{t_uid}" target="_blank" class="btn-sm btn-secondary">{p_emoji('lightning', 'Test Scan')} Test Scan</a>
            </td>
        </tr>
        """

    # Generate Reports Rows
    report_rows_html = ""
    for r in reports:
        r_id = r["id"]
        r_dog = html.escape(r.get("dog_name") or r.get("dog_uid") or "Campus Dog")
        r_type = html.escape(r.get("report_type", "INJURED"))
        r_sev = html.escape(r.get("severity", "MEDIUM"))
        r_status = html.escape(r.get("status", "PENDING"))
        r_loc = html.escape(r.get("campus_loc_name") or "Campus Ground")
        r_desc = html.escape(r.get("description", ""))
        r_by = html.escape(r.get("submitted_by", "Anonymous"))
        r_sev_class = "badge-red" if r_sev in ("CRITICAL", "HIGH") else "badge-yellow"

        report_rows_html += f"""
        <tr class="data-row">
            <td>
                <strong>{r_dog}</strong>
                <div style="font-size: 12px; color: #64748b;">{r_loc}</div>
            </td>
            <td>
                <span class="status-badge {r_sev_class}">{r_sev}</span>
                <span style="font-size: 12px; margin-left: 4px;">{r_type}</span>
            </td>
            <td style="max-width: 280px; font-size: 13px;">
                "{r_desc}"
                <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Reported by: {r_by}</div>
            </td>
            <td>
                <span class="status-badge badge-yellow">{r_status}</span>
            </td>
            <td style="text-align: right;">
                <button type="button" class="btn-sm btn-primary" onclick="updateReportStatus({r_id}, 'RESOLVED')">✔ Mark Resolved</button>
            </td>
        </tr>
        """
    if not report_rows_html:
        report_rows_html = '<tr><td colspan="5" style="text-align:center; padding: 24px; color: #64748b;">No active emergency reports. All campus dogs are safe! 🐾</td></tr>'

    loc_rows = []
    for l in locations:
        l_name = html.escape(l.get("name") or "Campus Location")
        l_type = html.escape(l.get("area_type") or "CAMPUS")
        lat = l.get("latitude")
        lon = l.get("longitude")
        if lat is not None and lon is not None:
            coord_str = f"{float(lat):.4f}° N, {float(lon):.4f}° E"
        else:
            coord_str = "Campus Grounds"
        l_desc = html.escape(l.get("description") or "")
        loc_rows.append(f'<tr><td><strong>{l_name}</strong></td><td><span class="tag-pill">{l_type}</span></td><td style="font-family: monospace; font-size: 12px;">{coord_str}</td><td style="color: #94a3b8; font-size: 13px;">{l_desc}</td></tr>')
    location_rows_html = "".join(loc_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOGCU Admin Portal — Chandigarh University</title>
    <style>
        :root {{
            --cu-red: #c41e3a;
            --bg-color: #0b1120;
            --card-bg: #1e293b;
            --card-sub: #0f172a;
            --border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
        }}
        .navbar {{
            background: #1e293b;
            border-bottom: 1px solid #334155;
            padding: 14px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
        }}
        .brand-group {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .cu-logo-badge {{
            background: #dc2626;
            color: white;
            font-weight: 800;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 6px;
            letter-spacing: 1px;
        }}
        .brand-name {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
        }}
        .user-nav {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .user-pill {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 9999px;
            padding: 4px 12px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .role-tag {{
            background: #374151;
            color: #facc15;
            font-size: 10px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .btn-nav {{
            color: #cbd5e1;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 8px;
            transition: all 0.2s ease;
        }}
        .btn-nav:hover {{
            background: #334155;
            color: white;
        }}
        .btn-logout {{
            background: #450a0a;
            color: #fca5a5;
            border: 1px solid #b91c1c;
        }}
        .btn-logout:hover {{
            background: #dc2626;
            color: white;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .stat-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            background: #0f172a;
            border: 1px solid var(--border);
        }}
        .stat-val {{
            font-size: 26px;
            font-weight: 800;
            color: white;
            line-height: 1;
        }}
        .stat-label {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .tabs-nav {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        .tab-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 700;
            padding: 10px 18px;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .tab-btn:hover {{
            color: white;
        }}
        .tab-btn.active {{
            color: #ef4444;
            border-bottom-color: #ef4444;
        }}
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 800;
            color: white;
        }}
        .table-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}
        th {{
            background: #0f172a;
            padding: 14px 16px;
            color: #94a3b8;
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid var(--border);
        }}
        td {{
            padding: 14px 16px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.5);
            vertical-align: middle;
        }}
        .data-row:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}
        .dog-thumb {{
            width: 44px;
            height: 44px;
            border-radius: 8px;
            object-fit: cover;
            border: 1px solid var(--border);
            background: #0f172a;
        }}
        .tag-pill {{
            background: #1e1b4b;
            color: #a5b4fc;
            border: 1px solid #4338ca;
            font-family: monospace;
            font-size: 12px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
        }}
        .health-pill {{
            background: #064e3b;
            color: #a7f3d0;
            font-size: 12px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
        }}
        .status-badge {{
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
        }}
        .badge-green {{ background: #065f46; color: #6ee7b7; }}
        .badge-yellow {{ background: #854d0e; color: #fde047; }}
        .badge-red {{ background: #991b1b; color: #fca5a5; }}
        .btn-sm {{
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 700;
            border-radius: 6px;
            cursor: pointer;
            border: none;
            text-decoration: none;
            display: inline-block;
            transition: all 0.15s ease;
        }}
        .btn-primary {{
            background: #dc2626;
            color: white;
        }}
        .btn-primary:hover {{
            background: #b91c1c;
        }}
        .btn-outline {{
            background: transparent;
            border: 1px solid #475569;
            color: #cbd5e1;
        }}
        .btn-outline:hover {{
            background: #334155;
            color: white;
        }}
        .btn-secondary {{
            background: #334155;
            color: white;
        }}
        .btn-secondary:hover {{
            background: #475569;
        }}
        .modal-overlay {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
            padding: 20px;
        }}
        .modal-overlay.active {{
            display: flex;
        }}
        .modal-box {{
            background: #1e293b;
            border: 1px solid #475569;
            border-radius: 16px;
            max-width: 520px;
            width: 100%;
            padding: 28px;
            max-height: 90vh;
            overflow-y: auto;
        }}
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .modal-close {{
            background: none;
            border: none;
            color: #94a3b8;
            font-size: 20px;
            cursor: pointer;
        }}
        .input-group {{
            margin-bottom: 16px;
        }}
        .input-group label {{
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 6px;
        }}
        .input-group input, .input-group select, .input-group textarea {{
            width: 100%;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px 12px;
            color: white;
            font-size: 14px;
            outline: none;
        }}
        .input-group input:focus, .input-group select:focus, .input-group textarea:focus {{
            border-color: #ef4444;
        }}
        .flash-toast {{
            background: #065f46;
            color: #a7f3d0;
            border: 1px solid #10b981;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            font-weight: 600;
        }}
        .premium-emoji {{
            display: inline-block;
            vertical-align: -0.2em;
            width: 1.25em;
            height: 1.25em;
            object-fit: contain;
            pointer-events: none;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.15));
        }}
        .premium-emoji--sm {{ width: 1.05em; height: 1.05em; }}
        .premium-emoji--md {{ width: 1.35em; height: 1.35em; }}
        .premium-emoji--lg {{ width: 1.75em; height: 1.75em; }}
        .stat-icon .premium-emoji {{
            width: 32px;
            height: 32px;
            vertical-align: middle;
        }}
        .tab-btn .premium-emoji {{
            margin-right: 6px;
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="brand-group">
            <span class="cu-logo-badge">DOGCU</span>
            <span class="brand-name">Campus Dog Identity System • Admin Portal</span>
        </div>
        <div class="user-nav">
            <div class="user-pill">
                <span>{p_emoji('user', 'User')} {user_name}</span>
                <span class="role-tag">{user_role}</span>
            </div>
            <a href="/" class="btn-nav" target="_blank">{p_emoji('globe', 'Public Site')} Public Site</a>
            <a href="/admin/logout" class="btn-nav btn-logout">Log Out</a>
        </div>
    </nav>

    <main class="container">
        {clean_msg}

        <!-- Metrics Overview -->
        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">{p_emoji('dog', 'Dogs')}</div>
                <div>
                    <div class="stat-val">{total_dogs}</div>
                    <div class="stat-label">Registered Dogs</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">{p_emoji('tag', 'Tags')}</div>
                <div>
                    <div class="stat-val">{assigned_tags} / {total_tags}</div>
                    <div class="stat-label">Active QR Collars</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">{p_emoji('pin', 'Sightings')}</div>
                <div>
                    <div class="stat-val">{total_sightings}</div>
                    <div class="stat-label">Sightings Logged</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">{p_emoji('siren', 'Emergency Reports')}</div>
                <div>
                    <div class="stat-val" style="color: {'#ef4444' if pending_reports > 0 else '#10b981'};">{pending_reports}</div>
                    <div class="stat-label">Pending Reports</div>
                </div>
            </div>
        </section>

        <!-- Tab Controls -->
        <div class="tabs-nav">
            <button type="button" class="tab-btn active" onclick="switchTab('dogs')">{p_emoji('dog', 'Dogs')} Manage Dogs</button>
            <button type="button" class="tab-btn" onclick="switchTab('tags')">{p_emoji('tag', 'Tags')} QR Collar Tags</button>
            <button type="button" class="tab-btn" onclick="switchTab('reports')">{p_emoji('siren', 'Reports')} Emergency Reports ({pending_reports})</button>
            <button type="button" class="tab-btn" onclick="switchTab('locations')">{p_emoji('school', 'Locations')} Campus Locations ({len(locations)})</button>
        </div>

        <!-- TAB 1: DOGS -->
        <div id="tab-dogs" class="tab-content">
            <div class="section-header">
                <h2 class="section-title">Registered Campus Dogs</h2>
                <button type="button" class="btn-sm btn-primary" onclick="openRegisterDogModal()">+ Register New Dog</button>
            </div>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>Photo</th>
                            <th>Dog Name &amp; ID</th>
                            <th>Active Tag</th>
                            <th>Gender &amp; Age</th>
                            <th>Health</th>
                            <th>Status</th>
                            <th style="text-align: right;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dog_rows_html}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB 2: TAGS -->
        <div id="tab-tags" class="tab-content" style="display: none;">
            <div class="section-header">
                <h2 class="section-title">Physical QR Collar Tags</h2>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <a href="/print/qr-sheet" target="_blank" class="btn-sm" style="background: #991b1b; color: white; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 8px; font-weight: 700;">
                        {p_emoji('printer', 'Print')} Print A4 Sheet (10 Collar Tags)
                    </a>
                    <form method="POST" action="/admin/tags/create" style="display: inline;">
                        <button type="submit" class="btn-sm btn-primary">+ Generate New QR Tag</button>
                    </form>
                </div>
            </div>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>Tag Identifier (Collar UID)</th>
                            <th>Tag Status</th>
                            <th>Assigned Campus Dog</th>
                            <th style="text-align: right;">Printing &amp; Resolution</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tag_rows_html}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB 3: REPORTS -->
        <div id="tab-reports" class="tab-content" style="display: none;">
            <div class="section-header">
                <h2 class="section-title">Welfare &amp; Injury Reports</h2>
            </div>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>Dog &amp; Spot</th>
                            <th>Severity &amp; Type</th>
                            <th>Situation Details</th>
                            <th>Status</th>
                            <th style="text-align: right;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {report_rows_html}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB 4: LOCATIONS -->
        <div id="tab-locations" class="tab-content" style="display: none;">
            <div class="section-header">
                <h2 class="section-title">Chandigarh University Campus Hotspots</h2>
            </div>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>Location Name</th>
                            <th>Area Type</th>
                            <th>Coordinates</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {location_rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- Modal: Register Dog -->
    <div class="modal-overlay" id="register-dog-modal">
        <div class="modal-box">
            <div class="modal-header">
                <h3 style="font-size: 18px; font-weight: 800;">Register New Campus Dog</h3>
                <button type="button" class="modal-close" onclick="closeModal('register-dog-modal')">✕</button>
            </div>
            <form method="POST" action="/admin/dogs/create">
                <div class="input-group">
                    <label>Dog Name *</label>
                    <input type="text" name="name" required placeholder="e.g. Rocky">
                </div>
                <div class="input-group">
                    <label>Gender *</label>
                    <select name="gender">
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Unknown">Unknown</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Approximate Age *</label>
                    <input type="text" name="approx_age" required placeholder="e.g. 2 years">
                </div>
                <div class="input-group">
                    <label>Photo URL (or choose /static/assets/dogs/...)</label>
                    <input type="text" name="photo_url" placeholder="/static/assets/dogs/bruno.png" value="/static/assets/dogs/bruno.png">
                </div>
                <div class="input-group">
                    <label>Personality / Quote</label>
                    <input type="text" name="description" placeholder="e.g. Calm, friendly with hostel students">
                </div>
                <button type="submit" class="btn-sm btn-primary" style="width: 100%; padding: 12px; font-size: 14px;">Register Dog ➔</button>
            </form>
        </div>
    </div>

    <!-- Modal: Edit Dog -->
    <div class="modal-overlay" id="edit-dog-modal">
        <div class="modal-box">
            <div class="modal-header">
                <h3 style="font-size: 18px; font-weight: 800;">Edit Dog Master Profile</h3>
                <button type="button" class="modal-close" onclick="closeModal('edit-dog-modal')">✕</button>
            </div>
            <form method="POST" action="/admin/dogs/update" id="edit-dog-form">
                <input type="hidden" name="dog_id" id="edit-dog-id">
                <div class="input-group">
                    <label>Dog Name</label>
                    <input type="text" name="name" id="edit-dog-name" required>
                </div>
                <div class="input-group">
                    <label>Gender</label>
                    <select name="gender" id="edit-dog-gender">
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Unknown">Unknown</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Approx Age</label>
                    <input type="text" name="approx_age" id="edit-dog-age" required>
                </div>
                <div class="input-group">
                    <label>Status</label>
                    <select name="status" id="edit-dog-status">
                        <option value="ACTIVE">ACTIVE</option>
                        <option value="UNDER_CARE">UNDER_CARE</option>
                        <option value="MISSING">MISSING</option>
                        <option value="ADOPTED">ADOPTED</option>
                        <option value="RETIRED">RETIRED</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Photo URL</label>
                    <input type="text" name="photo_url" id="edit-dog-photo">
                </div>
                <div class="input-group">
                    <label>Personality / Quote</label>
                    <input type="text" name="description" id="edit-dog-desc">
                </div>
                <button type="submit" class="btn-sm btn-primary" style="width: 100%; padding: 12px; font-size: 14px;">Save Changes ➔</button>
            </form>
        </div>
    </div>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            event.target.classList.add('active');
            document.getElementById('tab-' + tabId).style.display = 'block';
        }}

        function openRegisterDogModal() {{
            document.getElementById('register-dog-modal').classList.add('active');
        }}

        function openEditDogModal(id, name, uid, gender, age, status, photo, desc) {{
            document.getElementById('edit-dog-id').value = id;
            document.getElementById('edit-dog-name').value = name;
            document.getElementById('edit-dog-gender').value = gender;
            document.getElementById('edit-dog-age').value = age;
            document.getElementById('edit-dog-status').value = status;
            document.getElementById('edit-dog-photo').value = photo;
            document.getElementById('edit-dog-desc').value = desc || '';
            document.getElementById('edit-dog-modal').classList.add('active');
        }}

        function closeModal(id) {{
            document.getElementById(id).classList.remove('active');
        }}

        async function updateReportStatus(reportId, newStatus) {{
            if (!confirm('Mark report #' + reportId + ' as ' + newStatus + '?')) return;
            try {{
                const res = await fetch('/api/admin/reports/' + reportId + '/status', {{
                    method: 'PATCH',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ status: newStatus }})
                }});
                if (res.ok) {{
                    location.reload();
                }} else {{
                    alert('Could not update report status.');
                }}
            }} catch (err) {{
                alert('Network error: ' + err.message);
            }}
        }}
    </script>
</body>
</html>
"""
