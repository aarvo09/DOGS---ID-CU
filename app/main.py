import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
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

@app.get("/", tags=["Public"])
async def root_redirect(request: Request):
    """
    Public root entrypoint:
    Directly redirects public visitors to the official campus dog profile (Bruno / CU-DOG-024).
    If an admin is logged in, redirects directly into the Admin Management Portal (/admin).
    """
    admin = get_optional_admin(request)
    if admin:
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/dog/CU-DOG-024", status_code=status.HTTP_303_SEE_OTHER)



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


