import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME, APP_VERSION, UPLOAD_DIR
from app.database import get_db, init_db
from app.middleware import SecurityHeadersMiddleware
from app.seed import seed_database
from app.dog_view import render_handwritten_dog_profile, render_dog_not_found, p_emoji
from app.dog_service import get_dog_profile
from app.components_view import render_component_showcase
from app.utils import resolve_last_seen_for_dog, resolve_health_overview, format_time_ago

# Routers
from app.routes.qr import router as qr_router
from app.routes.public import router as public_router
from app.routes.auth import router as auth_router
from app.routes.admin_dogs import router as admin_dogs_router
from app.routes.admin_tags import router as admin_tags_router
from app.routes.admin_sightings import router as admin_sightings_router
from app.routes.admin_reports import router as admin_reports_router
from app.routes.admin_locations import router as admin_locations_router
from app.routes.admin_users import router as admin_users_router
from app.routes.admin_dashboard import router as admin_dashboard_router
from app.routes.admin_ui import router as admin_ui_router
from app.routes.upload import router as upload_router
from app.security import get_optional_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    init_db()
    # Auto-seed if empty
    seed_database()
    yield

app = FastAPI(
    title=APP_NAME,
    description="Backend Architecture & API for Chandigarh University Campus Dog Digital Identity System",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware (Allows frontends to integrate smoothly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Serve static assets (hand-drawn field notebook styles, scripts, illustrations)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(qr_router)
app.include_router(public_router)
app.include_router(auth_router)
app.include_router(admin_dogs_router)
app.include_router(admin_tags_router)
app.include_router(admin_sightings_router)
app.include_router(admin_reports_router)
app.include_router(admin_locations_router)
app.include_router(admin_users_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_ui_router)
app.include_router(upload_router)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "HEALTHY",
        "service": APP_NAME,
        "version": APP_VERSION,
    }

@app.get("/", response_class=HTMLResponse, tags=["System"])
async def system_index():
    """System overview and interactive workbench link."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chandigarh University - Campus Dog Digital Identity System</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            max-width: 800px;
            width: 100%;
        }
        .card {
            background: #1e293b;
            border-radius: 16px;
            border: 1px solid #334155;
            padding: 32px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
        }
        .badge {
            display: inline-block;
            background: #dc2626;
            color: white;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 9999px;
            margin-bottom: 16px;
        }
        h1 {
            font-size: 26px;
            font-weight: 800;
            margin: 0 0 12px 0;
            letter-spacing: -0.5px;
            color: #ffffff;
        }
        p {
            font-size: 15px;
            color: #94a3b8;
            line-height: 1.6;
            margin: 0 0 24px 0;
        }
        .links-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .link-card {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            text-decoration: none;
            color: #f8fafc;
            transition: all 0.2s ease;
        }
        .link-card:hover {
            border-color: #38bdf8;
            transform: translateY(-2px);
        }
        .link-title {
            font-weight: 700;
            font-size: 15px;
            color: #38bdf8;
            margin-bottom: 6px;
        }
        .link-desc {
            font-size: 12px;
            color: #64748b;
        }
        .premium-emoji {
            display: inline-block;
            vertical-align: -0.2em;
            width: 1.25em;
            height: 1.25em;
            object-fit: contain;
            pointer-events: none;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.15));
            margin-right: 4px;
        }
        .tag-demo {
            background: #090d16;
            border-radius: 10px;
            padding: 16px;
            border: 1px solid #1e293b;
        }
        .tag-title {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #e2e8f0;
            margin-bottom: 10px;
        }
        .code-chip {
            display: inline-block;
            background: #1e293b;
            color: #fbbf24;
            font-family: monospace;
            padding: 4px 8px;
            border-radius: 6px;
            margin-right: 8px;
            margin-bottom: 6px;
            text-decoration: none;
            font-size: 13px;
        }
        .code-chip:hover {
            background: #334155;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <span class="badge">Backend Active</span>
            <h1>Chandigarh University Campus Dog Digital Identity System</h1>
            <p>
                Core high-performance backend serving the physical QR resolution system, public dog profile and sighting reports, 
                and authenticated administrative controls for dog registration, tag management, and animal welfare.
            </p>

            <div class="links-grid">
                <a href="/admin" class="link-card" style="border-color: #3b82f6;">
                    <div class="link-title" style="color: #60a5fa;"><img src="/static/assets/emojis/crown.webp" class="premium-emoji" alt="Admin" draggable="false" /> Admin Management Portal</div>
                    <div class="link-desc">Manage dogs, edit profiles, register tags, view sightings, and resolve welfare reports.</div>
                </a>
                <a href="/dog/CU-DOG-024" class="link-card" style="border-color: #f59e0b;">
                    <div class="link-title" style="color: #f59e0b;"><img src="/static/assets/emojis/notebook.webp" class="premium-emoji" alt="Notebook" draggable="false" /> Bruno's Field Notebook</div>
                    <div class="link-desc">Live hand-drawn digital profile for CU-DOG-024.</div>
                </a>
                <a href="/components" class="link-card" style="border-color: #dc2626;">
                    <div class="link-title" style="color: #ef4444;"><img src="/static/assets/emojis/palette.webp" class="premium-emoji" alt="Palette" draggable="false" /> Component Showcase &amp; Assets</div>
                    <div class="link-desc">Interactive workbench of all 9 hand-drawn field notebook visual components and asset catalog.</div>
                </a>
                <a href="/docs" class="link-card">
                    <div class="link-title"><img src="/static/assets/emojis/lightning.webp" class="premium-emoji" alt="API Docs" draggable="false" /> Interactive Swagger UI</div>
                    <div class="link-desc">Test all public and admin endpoints directly in your browser.</div>
                </a>
                <a href="/t/CU-TAG-8F42K9" class="link-card">
                    <div class="link-title"><img src="/static/assets/emojis/tag.webp" class="premium-emoji" alt="Collar Tag" draggable="false" /> Permanent QR Scan</div>
                    <div class="link-desc">Resolves CU-TAG-8F42K9 directly to Bruno's profile.</div>
                </a>
            </div>

            <div class="tag-demo">
                <div class="tag-title">Demo Physical QR Tag Links to Test:</div>
                <a href="/t/CU-TAG-8F42K9?format=json" class="code-chip">/t/CU-TAG-8F42K9 (Bruno)</a>
                <a href="/t/CU-TAG-9M31P2?format=json" class="code-chip">/t/CU-TAG-9M31P2 (Milo)</a>
                <a href="/t/CU-TAG-4K77X1?format=json" class="code-chip">/t/CU-TAG-4K77X1 (Luna)</a>
                <a href="/t/CU-TAG-SPAREE?format=json" class="code-chip">/t/CU-TAG-SPAREE (Unassigned)</a>
                <a href="/t/CU-TAG-NONEXIST?format=json" class="code-chip">/t/CU-TAG-NONEXIST (Invalid)</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/components", response_class=HTMLResponse, tags=["Design System"])
async def components_showcase():
    """
    Component Showcase: Interactive visual workbench displaying the 9 core
    hand-drawn field notebook components and the organized asset library.
    """
    return HTMLResponse(content=render_component_showcase())

@app.get("/dog/{dog_uid}", response_class=HTMLResponse, tags=["Public"])
async def public_dog_page(request: Request, dog_uid: str):
    """
    Public profile page: Hand-Drawn Campus Dog Field Notebook.
    Represents ONE specific dog driven by dogId.
    If an admin is logged in, unlocks in-page profile editing & admin toolbar.
    """
    clean_uid = dog_uid.strip().upper()
    dog_data = get_dog_profile(clean_uid)

    if not dog_data:
        return HTMLResponse(content=render_dog_not_found(clean_uid), status_code=404)

    admin_user = get_optional_admin(request)
    html_content = render_handwritten_dog_profile(dog_data, admin_user=admin_user)
    return HTMLResponse(content=html_content)

@app.get("/dog/{dog_uid}/sighting", tags=["Public"])
async def public_dog_sighting_redirect(dog_uid: str):
    """Direct URL for reporting a sighting for a specific dog."""
    clean_uid = dog_uid.strip().upper()
    return RedirectResponse(url=f"/dog/{clean_uid}?modal=sighting", status_code=302)

@app.get("/dog/{dog_uid}/report", tags=["Public"])
async def public_dog_report_redirect(dog_uid: str):
    """Direct URL for reporting an injury or issue for a specific dog."""
    clean_uid = dog_uid.strip().upper()
    return RedirectResponse(url=f"/dog/{clean_uid}?modal=report", status_code=302)

@app.get("/dog/{dog_uid}/location", tags=["Public"])
async def public_dog_location_redirect(dog_uid: str):
    """Direct URL for viewing the last-seen location on the campus map for a specific dog."""
    clean_uid = dog_uid.strip().upper()
    return RedirectResponse(url=f"/dog/{clean_uid}#last-spotted-section", status_code=302)


