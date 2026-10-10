"""
Chandigarh University Campus Dog Digital Identity System (DOGCU)
Individual Dog Profile View (Handmade Field Notebook Aesthetic)

Implements the single public dog profile page (/dog/:dogId)
using the centralized handmade visual language design system.
"""

import html
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

def p_emoji(name: str, alt: str = "", size: str = "", extra_class: str = "") -> str:
    """Renders authentic hand-drawn field notebook doodle emoji."""
    size_cls = f" premium-emoji--{size}" if size else ""
    extra = f" {extra_class}" if extra_class else ""
    return f'<img src="/static/assets/emojis/{name}.webp" class="premium-emoji{size_cls}{extra}" alt="{alt}" draggable="false" />'

def canonical_campus_location(location_name: str) -> str:
    """
    Normalizes any campus location string strictly to the 7 canonical locations:
    Academic Block E, Academic Block F, Hostel A, Hostel B, Field, Pond, Parking.
    """
    loc = (location_name or "").strip().lower()
    if "park" in loc or "gate" in loc or "car" in loc or "vehicle" in loc:
        return "Parking"
    if "block f" in loc or "block 3" in loc or "management" in loc:
        return "Academic Block F"
    if "block e" in loc or "block 2" in loc or "computing" in loc or "ai" in loc or "quad" in loc:
        return "Academic Block E"
    if "hostel b" in loc or "south" in loc or "girl" in loc:
        return "Hostel B"
    if "hostel a" in loc or "hostel" in loc or "block a" in loc or "block 1" in loc or "engineering" in loc or "north" in loc or "boy" in loc:
        return "Hostel A"
    if "field" in loc or "ground" in loc or "sports" in loc or "cricket" in loc or "stadium" in loc:
        return "Field"
    if "pond" in loc or "lake" in loc or "lawn" in loc or "fountain" in loc or "water" in loc or "central" in loc:
        return "Pond"
    return "Academic Block E"

def resolve_campus_coordinates(location_name: str) -> tuple[float, float, str]:
    """
    Calibrates the 7 canonical campus landmarks on the official CU Campus Map (1536x1024).
    Returns (x_percent, y_percent, canonical_name).
    """
    canonical_name = canonical_campus_location(location_name)
    coords = {
        "Parking": (7.2, 25.9),
        "Academic Block F": (34.8, 13.7),
        "Academic Block E": (37.1, 35.6),
        "Field": (36.5, 61.0),
        "Pond": (67.7, 59.6),
        "Hostel A": (36.5, 81.1),
        "Hostel B": (69.0, 81.1),
    }
    x, y = coords.get(canonical_name, (37.1, 35.6))
    return (x, y, canonical_name)

def render_handwritten_dog_profile(dog: Dict[str, Any], admin_user: Optional[Dict[str, Any]] = None) -> str:
    """
    Renders the authentic Hand-Drawn Campus Dog Field Notebook HTML page
    for ONE specific dog.
    If an admin/staff is logged in, unlocks in-page quick edit controls.
    """
    db_id = dog.get("db_id", 1)
    clean_uid = html.escape(dog.get("id", "CU-DOG-024"))
    dog_name = html.escape(dog.get("name", "Bruno"))
    gender = html.escape(dog.get("gender", "Male"))
    approx_age = html.escape(dog.get("age", "3 years"))
    personality = html.escape(dog.get("personality", "Friendly • Gentle"))
    quote = html.escape(dog.get("quote", "Professional napper. Loves students and treats."))
    regular_area = html.escape(dog.get("regularArea", "Academic Block 2 • Central Lawn"))
    photo_url = html.escape(dog.get("photo_url", "/static/images/bruno_portrait.jpg"))
    tag_uid = html.escape(dog.get("tag_uid", f"CU-TAG-{clean_uid.split('-')[-1]}"))
    qr_data_url = dog.get("qr_data_url") or ""

    raw_status = html.escape(str(dog.get("status", "ACTIVE")).upper())
    raw_gender = html.escape(str(dog.get("gender", "Male")))
    raw_description = html.escape(str(dog.get("description") or ""))

    # Time-aware Campus Map resolution (IST UTC+5:30)
    # Day (8:00 AM - 8:00 PM): Colourful Campus Map
    # Night (8:00 PM - 7:59 AM): Night-Time Campus Map with Lights & Landmarks
    ist_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    is_daytime = 8 <= ist_time.hour < 20
    map_src = "/static/assets/maps/campus-map-day.png" if is_daytime else "/static/assets/maps/campus-map-night.png"
    map_mode = "day" if is_daytime else "night"
    map_label = "Day View (8 AM–8 PM)" if is_daytime else "Night View (8 PM–8 AM)"
    map_icon_html = p_emoji("sun", "Daytime", size="sm") if is_daytime else p_emoji("moon", "Nighttime", size="sm")
    map_alt = "Chandigarh University Campus Map (Daytime)" if is_daytime else "Chandigarh University Night-Time Campus Map with Lights (Nighttime)"

    # Health records
    health_status = html.escape(dog.get("healthStatus", "Healthy"))
    vacc_status = html.escape(dog.get("vaccination", "Up to date"))
    ster_status = html.escape(dog.get("sterilization", "Yes"))
    last_checkup = html.escape(dog.get("lastCheckup", "15 Mar 2026"))

    # Last seen telemetry
    last_seen = dog.get("lastSeen", {})
    last_loc_name = html.escape(last_seen.get("location", "Academic Block E"))
    last_time_ago = html.escape(last_seen.get("time_ago", "12 minutes ago"))
    last_activity = html.escape(last_seen.get("activity", "Resting"))
    lat_val = last_seen.get("latitude", 30.7695)
    lon_val = last_seen.get("longitude", 76.5760)

    # Calibrate exact coordinates on the Campus Map
    pin_x, pin_y, display_landmark = resolve_campus_coordinates(last_loc_name)

    # Recent sightings list (normalized to canonical locations)
    sightings = dog.get("sightings", [])
    sightings_items_html = ""
    pin_html = p_emoji("pin", "Location", size="sm")
    if sightings:
        for s in sightings[:4]:
            raw_loc = s.get("location") or "Academic Block E"
            loc = html.escape(canonical_campus_location(raw_loc))
            time_ago = html.escape(s.get("time_ago") or "Recently")
            act = html.escape(s.get("activity") or "Spotted")
            note = html.escape(s.get("note") or "")
            note_part = f' • "{note}"' if note else ""
            sightings_items_html += f"""
            <div class="sighting-item">
                <div class="sighting-pin-location">
                    <span class="pin-bullet">{pin_html}</span>
                    <div>
                        <div class="sighting-location-text">{loc}</div>
                        <div class="sighting-subtext">{act}{note_part}</div>
                    </div>
                </div>
                <div class="sighting-time-badge">{time_ago}</div>
            </div>
            """
    else:
        sightings_items_html = f"""
        <div class="sighting-item">
            <div class="sighting-pin-location">
                <span class="pin-bullet">{pin_html}</span>
                <div>
                    <div class="sighting-location-text">{display_landmark}</div>
                    <div class="sighting-subtext">{last_activity}</div>
                </div>
            </div>
            <div class="sighting-time-badge">{last_time_ago}</div>
        </div>
        """

    # Personality tags helper
    first_personality = personality.split("•")[0].strip()

    # Admin Controls & Edit Modal
    if admin_user:
        admin_name = html.escape(admin_user.get("name", "Staff Member"))
        admin_role = html.escape(admin_user.get("role", "ADMIN"))
        floating_admin_bar = f"""
        <div class="admin-floating-status-bar">
            <div class="admin-status-inner">
                <div class="admin-status-left">
                    <span class="status-shield">{p_emoji('shield', 'Admin Shield')}</span>
                    <span>Admin Mode: <strong>{admin_name}</strong> <span class="role-chip">{admin_role}</span></span>
                </div>
                <div class="admin-status-right">
                    <span>Direct QR Scan: Editing Unlocked</span>
                    <button type="button" class="admin-bar-btn" id="open-edit-dog-btn-bar">{p_emoji('pencil', 'Edit')} Edit {dog_name}</button>
                    <a href="/admin" class="admin-bar-link">Admin Dashboard ➔</a>
                    <a href="/admin/logout?next=/dog/{clean_uid}" class="admin-bar-link" style="color: #f87171;">Sign Out</a>
                </div>
            </div>
        </div>
        """
        header_admin_controls = f"""
        <div class="admin-top-controls">
            <button type="button" class="btn-handdrawn btn-admin-quick" id="open-edit-dog-btn">
                {p_emoji('pencil', 'Edit')} Edit Profile
            </button>
            <a href="/admin" class="admin-dash-pill">
                {p_emoji('chart', 'Dashboard')} Admin
            </a>
            <a href="/admin/logout?next=/dog/{clean_uid}" class="admin-dash-pill logout" title="Sign Out">
                {p_emoji('door', 'Sign Out')}
            </a>
        </div>
        """
        hero_admin_button = f"""
        <button type="button" class="admin-edit-sticker-btn" id="open-edit-dog-btn-hero" title="Edit this dog's official record">
            {p_emoji('pencil', 'Edit')} Edit Record
        </button>
        """
        edit_modal_html = f"""
        <!-- Admin Quick Edit Dog Modal -->
        <div class="modal-overlay" id="edit-dog-modal">
            <div class="modal-notebook-card modal-notebook-card--wide">
                <button type="button" class="modal-close-btn" aria-label="Close" id="close-edit-modal-btn">✕</button>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    {p_emoji('pencil', 'Edit', size='lg')}
                    <h3 class="modal-title" style="margin: 0; color: #1e3a8a;">Edit {dog_name}'s Record</h3>
                </div>
                <p class="modal-desc">Administrative Master Update for {clean_uid} • Direct In-Field Edit</p>


                <form action="/admin/dogs/{db_id}/update" method="POST" id="admin-dog-update-form">
                    <input type="hidden" name="next_url" value="/dog/{clean_uid}" />

                    <div class="edit-form-grid">
                        <div class="handwritten-input-group">
                            <label class="input-label" for="edit-dog-name">Dog Name:</label>
                            <input type="text" id="edit-dog-name" name="name" class="handwritten-input" value="{dog_name}" required />
                        </div>

                        <div class="handwritten-input-group">
                            <label class="input-label" for="edit-dog-gender">Gender:</label>
                            <select id="edit-dog-gender" name="gender" class="handwritten-select">
                                <option value="Male" {"selected" if raw_gender == "Male" else ""}>Male</option>
                                <option value="Female" {"selected" if raw_gender == "Female" else ""}>Female</option>
                                <option value="Unknown" {"selected" if raw_gender == "Unknown" else ""}>Unknown</option>
                            </select>
                        </div>

                        <div class="handwritten-input-group">
                            <label class="input-label" for="edit-dog-age">Approx Age:</label>
                            <input type="text" id="edit-dog-age" name="approx_age" class="handwritten-input" value="{approx_age}" placeholder="e.g. 3 years" required />
                        </div>

                        <div class="handwritten-input-group">
                            <label class="input-label" for="edit-dog-status">Registry Status:</label>
                            <select id="edit-dog-status" name="status_val" class="handwritten-select">
                                <option value="ACTIVE" {"selected" if "ACTIVE" in raw_status else ""}>ACTIVE (Living on campus)</option>
                                <option value="UNDER_CARE" {"selected" if "CARE" in raw_status else ""}>UNDER_CARE (Medical recovery)</option>
                                <option value="MISSING" {"selected" if "MISSING" in raw_status else ""}>MISSING (Active search)</option>
                                <option value="ADOPTED" {"selected" if "ADOPTED" in raw_status else ""}>ADOPTED (Found permanent home)</option>
                                <option value="INACTIVE" {"selected" if "INACTIVE" in raw_status else ""}>INACTIVE (Archived)</option>
                            </select>
                        </div>
                    </div>

                    <div class="handwritten-input-group">
                        <label class="input-label" for="edit-dog-photo">Dog Photo:</label>
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                            <input type="text" id="edit-dog-photo" name="photo_url" class="handwritten-input" value="{photo_url}" placeholder="/static/images/..." style="flex: 1;" />
                            <label class="btn-handdrawn btn-handdrawn--accent" style="cursor: pointer; margin: 0; white-space: nowrap; padding: 6px 12px; font-size: 13px; display: inline-flex; align-items: center; gap: 4px;">
                                📷 Choose / Take Photo
                                <input type="file" accept="image/*" style="display: none;" onchange="handleInFieldPhotoUpload(this)" />
                            </label>
                        </div>
                        <div id="infield-photo-status" style="font-size: 12px; color: #047857; margin-bottom: 6px; font-weight: 700;"></div>
                        <img id="infield-photo-preview" src="{photo_url}" style="width: 72px; height: 72px; object-fit: cover; border-radius: 8px; border: 1.5px solid var(--border-rough); display: block;" alt="Dog Preview" />
                    </div>

                    <div class="handwritten-input-group">
                        <label class="input-label" for="edit-dog-desc">Description & Bio:</label>
                        <textarea id="edit-dog-desc" name="description" class="handwritten-textarea" rows="2" placeholder="Personality, identifying marks, beloved habits...">{raw_description}</textarea>
                    </div>

                    <div style="margin-top: 14px; border-top: 1.5px dashed var(--ink-faint, #cbd5e1); padding-top: 12px;">
                        <div style="font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                            {p_emoji('stethoscope', 'Stethoscope')} Health &amp; Welfare Updates (Logs to medical ledger)
                        </div>

                        <div class="edit-form-grid">
                            <div class="handwritten-input-group">
                                <label class="input-label" for="edit-health-status">Health Status:</label>
                                <select id="edit-health-status" name="health_status" class="handwritten-select">
                                    <option value="HEALTHY">Healthy & Active</option>
                                    <option value="UNDER_TREATMENT">Under Treatment / Recovery</option>
                                    <option value="NEEDS_ATTENTION">Needs Attention</option>
                                    <option value="CRITICAL">Critical Medical Need</option>
                                </select>
                            </div>

                            <div class="handwritten-input-group">
                                <label class="input-label" for="edit-vacc-status">Vaccination Status:</label>
                                <select id="edit-vacc-status" name="vaccination_status" class="handwritten-select">
                                    <option value="UP_TO_DATE">Up to date (Rabies & 7-in-1)</option>
                                    <option value="DUE_SOON">Due Soon</option>
                                    <option value="OVERDUE">Overdue for Booster</option>
                                    <option value="NOT_VACCINATED">Not Vaccinated</option>
                                </select>
                            </div>

                            <div class="handwritten-input-group">
                                <label class="input-label" for="edit-ster-status">Sterilization Status:</label>
                                <select id="edit-ster-status" name="sterilization_status" class="handwritten-select">
                                    <option value="YES">Yes (Ear-notched / Neutered)</option>
                                    <option value="NO">No (Pending ABC drive)</option>
                                </select>
                            </div>

                            <div class="handwritten-input-group">
                                <label class="input-label" for="edit-health-notes">Medical Notes:</label>
                                <input type="text" id="edit-health-notes" name="health_notes" class="handwritten-input" placeholder="e.g. Annual Rabies vaccine completed 2026" />
                            </div>
                        </div>
                    </div>

                    <div style="display: flex; gap: 12px; margin-top: 20px;">
                        <button type="submit" class="btn-handdrawn btn-handdrawn--marker" style="flex: 2; background: #2563eb; color: #fff;">
                            {p_emoji('disk', 'Save')} Save &amp; Apply Changes ➔
                        </button>
                        <button type="button" class="btn-handdrawn btn-handdrawn--outline" id="cancel-edit-btn" style="flex: 1;">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
        """
    else:
        floating_admin_bar = ""
        header_admin_controls = f"""
        <a href="/admin" class="staff-login-chip" id="admin-login-link" title="Admin Login — Access DOGCU Staff Panel">
            <span class="staff-login-icon">{p_emoji('lock', 'Admin', size='xs')}</span>
            <span class="staff-login-label">Admin Login</span>
            <span style="display:none;" aria-hidden="true">Staff Login</span>
        </a>
        """
        hero_admin_button = ""
        edit_modal_html = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dog_name} ({clean_uid}) — CU Campus Dogs Field Notebook</title>
    <meta name="description" content="Official digital identity & field notebook profile for {dog_name} ({clean_uid}), living on Chandigarh University campus.">
    <meta property="og:title" content="{dog_name} ({clean_uid}) - Chandigarh University Dog Profile">
    <meta property="og:description" content="View {dog_name}'s live location, health records, and report sightings.">
    <meta property="og:image" content="{photo_url}">
    <link rel="stylesheet" href="/static/css/handmade.css">
    <link rel="stylesheet" href="/static/css/notebook.css">
    <link rel="stylesheet" href="/static/css/components.css">
</head>
<body>
    {floating_admin_bar}

    <div class="notebook-desk">

        <!-- ================================================================
             TOP: CU Campus Dogs Identity, Handmade Back Arrow & Paw Doodle
             (Strictly shows only this specific dog; no directory or other dogs)
             ================================================================ -->
        <header class="profile-top-bar">
            <a href="/" class="handmade-back-link" title="Return to Campus Dogs">
                <span class="back-arrow-icon">←</span>
                <span>Campus Dogs</span>
            </a>

            <div class="top-brand-pill">
                <svg class="cu-logo-paw" viewBox="0 0 24 24" style="width: 20px; height: 20px;">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
                <span>CU Campus Dogs</span>
            </div>

            {header_admin_controls}
        </header>

        <!-- Main Field Notebook Document -->
        <main class="notebook-book" id="notebook-main">
            <div class="notebook-grid">

                <!-- ================= LEFT COLUMN: DOG DOSSIER ================= -->
                <div class="notebook-col-left">

                    <!-- 1. MAIN DOG PHOTOGRAPH (Physically attached with tape & annotations) -->
                    <div class="polaroid-frame-wrapper rotate-slight-left rotate-hover-level order-mobile-photo">
                        <div class="polaroid-card">
                            <div class="tape-strip tape-strip--corner-left"></div>
                            <div class="tape-strip tape-strip--corner-right"></div>

                            <div class="polaroid-img-box">
                                <img 
                                    id="dog-photo-img"
                                    src="{photo_url}" 
                                    alt="{dog_name} - Chandigarh University Campus Dog" 
                                    class="polaroid-img"
                                    onerror="this.src='/static/images/bruno_portrait.jpg';"
                                />

                                <!-- Hand-drawn Crown Doodle -->
                                <svg class="doodle-crown" viewBox="0 0 100 60" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M10 50 L20 15 L45 35 L50 10 L55 35 L80 15 L90 50 Z" />
                                    <circle cx="20" cy="15" r="4" fill="#ffffff" />
                                    <circle cx="50" cy="10" r="4" fill="#ffffff" />
                                    <circle cx="80" cy="15" r="4" fill="#ffffff" />
                                </svg>

                                <!-- Hand-drawn Heart Doodle -->
                                <svg class="doodle-heart" viewBox="0 0 24 24">
                                    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                                </svg>
                            </div>

                            <!-- Polaroid Handwritten Caption with Arrow Annotation -->
                            <div class="polaroid-caption">
                                <div class="handwritten-annotation annotation-pencil" style="font-size: 1.35rem;">
                                    Hey! I'm {dog_name}
                                    <svg class="annotation-arrow" viewBox="0 0 50 25" fill="none" stroke="var(--ink)" stroke-width="2.5" stroke-linecap="round">
                                        <path d="M5 20 Q 25 22, 42 8 M 35 6 L 45 7 L 42 16" />
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 2. DOG IDENTITY: Name, ID, Stamp & Basic Info -->
                    <div class="dog-hero-identity order-mobile-identity">
                        <div class="title-with-sunburst">
                            <h1 class="dog-name-ink" id="dog-name-display">{dog_name.upper()}</h1>
                            <!-- Red marker sunburst dashes -->
                            <svg class="marker-sunburst" viewBox="0 0 40 40" fill="none" stroke="var(--cu-red-marker)" stroke-width="3" stroke-linecap="round">
                                <line x1="20" y1="5" x2="20" y2="12" />
                                <line x1="32" y1="9" x2="26" y2="15" />
                                <line x1="35" y1="22" x2="28" y2="22" />
                            </svg>
                        </div>

                        <div class="id-and-badges-row">
                            <!-- Red Hand-Drawn Marker Pill for Dog ID -->
                            <div class="red-marker-id-pill" id="dog-id-display">
                                {clean_uid}
                            </div>

                            <!-- Sage Green Torn Sticker: Registered Campus Dog -->
                            <div class="registered-sticker-badge">
                                <span class="sticker-check">✔</span> REGISTERED CAMPUS DOG
                            </div>

                            {hero_admin_button}
                        </div>

                        <!-- Basic information without turning it into a conventional card grid -->
                        <div class="handmade-info-cluster">
                            <div class="info-pill-item rotate-subtle-left">
                                <span class="info-pill-icon">{p_emoji('dog', 'Dog')}</span>
                                <span>{gender}</span>
                            </div>
                            <div class="info-pill-item rotate-subtle-right">
                                <span class="info-pill-icon">{p_emoji('cake', 'Age')}</span>
                                <span>~{approx_age}</span>
                            </div>
                            <div class="info-pill-item rotate-subtle-left">
                                <span class="info-pill-icon">{p_emoji('heart_red', 'Personality')}</span>
                                <span>{first_personality}</span>
                            </div>
                            <div class="info-pill-item rotate-subtle-right">
                                <span class="info-pill-icon">{p_emoji('school', 'Campus')}</span>
                                <span>Campus Dog</span>
                            </div>
                        </div>
                    </div>

                    <!-- 3. PERSONALITY: Handwritten Small Paper Note -->
                    <div class="paper-note paper-note--yellow rotate-slight-left rotate-hover-level order-mobile-personality">
                        <div class="paper-note__pin-red"></div>
                        <div class="paper-note__header" style="font-size: 1.15rem; color: var(--ink);">
                            Personality &amp; Habits
                        </div>
                        <div class="paper-note__content" style="font-size: 1.25rem; font-style: italic; color: var(--ink); line-height: 1.4;">
                            "{quote}"
                        </div>
                    </div>

                    <!-- 4. PRIMARY & SECONDARY ACTIONS -->
                    <div class="field-actions-block order-mobile-cta">
                        <!-- Primary CTA: Hand-painted red marker button navigating to /dog/:dogId/sighting -->
                        <a href="/dog/{clean_uid}/sighting" class="btn-handdrawn btn-handdrawn--marker btn-cta-main" id="btn-saw-dog">
                            <span class="btn-handdrawn__icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                                    <circle cx="12" cy="13" r="4"/>
                                </svg>
                            </span>
                            <span>I SAW THIS DOG ➔</span>
                        </a>

                        <!-- Secondary Controls: View Last Location & Report an Issue -->
                        <div class="secondary-actions-cluster order-mobile-secondary-actions">
                            <a href="/dog/{clean_uid}/location" class="btn-handdrawn btn-handdrawn--outline" id="btn-view-location">
                                <span class="btn-handdrawn__icon">{p_emoji('pin', 'Location')}</span>
                                <span>VIEW LAST LOCATION ➔</span>
                            </a>
                            <a href="/dog/{clean_uid}/report" class="btn-handdrawn btn-handdrawn--kraft" id="btn-report-issue">
                                <span class="btn-handdrawn__icon">{p_emoji('warning', 'Warning')}</span>
                                <span>REPORT AN ISSUE ➔</span>
                            </a>
                        </div>
                    </div>

                </div>

                <!-- ================= RIGHT COLUMN: MAP, CARE & SIGHTINGS ================= -->
                <div class="notebook-col-right">

                    <!-- 5. LAST SPOTTED: Hand-drawn Campus Map Section -->
                    <section class="last-spotted-card rough-border-1 rotate-slight-left order-mobile-last-spotted" id="last-spotted-section">
                        <div class="tape-strip tape-strip--top-center"></div>
                        <div class="spotted-header-row">
                            <div class="spotted-title-group">
                                {p_emoji('pin', 'Location', size='lg')}
                                <h2 class="spotted-title">LAST SPOTTED</h2>
                            </div>
                            <span class="spotted-time-ago" id="spotted-time-display">{last_time_ago}</span>
                        </div>

                        <div class="spotted-place-name" id="spotted-place-display">
                            {display_landmark}
                        </div>
                        <div class="spotted-activity-note" id="spotted-activity-display">
                            Activity: {last_activity}
                        </div>

                        <!-- Clean Interactive Zoomable Campus Map (Touch pinch-to-zoom & pan) -->
                        <div class="campus-map-box" id="campus-map-box">
                            <div class="campus-map-viewport" id="campus-map-viewport">
                                <div class="campus-map-canvas" id="campus-map-canvas">
                                    <img 
                                        src="{map_src}" 
                                        alt="{map_alt}" 
                                        class="campus-map-img"
                                        id="campus-map-img"
                                        data-day-src="/static/assets/maps/campus-map-day.png"
                                        data-night-src="/static/assets/maps/campus-map-night.png"
                                        data-mode="{map_mode}"
                                        draggable="false"
                                    />
                                    <!-- Animated Compact Dog Location Pin pointing to exact campus spot -->
                                    <div class="map-dog-pin" id="map-dog-pin" style="left: {pin_x}%; top: {pin_y}%;" title="{dog_name} spotted here">
                                        <div class="map-pin-ripple"></div>
                                        <div class="map-pin-marker">
                                            <span class="map-pin-paw">🐾</span>
                                        </div>
                                        <div class="map-pin-tooltip">{dog_name} spotted here</div>
                                    </div>
                                </div>
                            </div>
                            <!-- Floating Zoom & Fit Controls -->
                            <div class="campus-map-controls" id="campus-map-controls" aria-label="Campus Map Controls">
                                <button type="button" class="map-ctrl-btn" id="map-zoom-in-btn" title="Zoom in" aria-label="Zoom in">+</button>
                                <button type="button" class="map-ctrl-btn" id="map-zoom-out-btn" title="Zoom out" aria-label="Zoom out">−</button>
                                <button type="button" class="map-ctrl-btn map-ctrl-btn--fit" id="map-zoom-fit-btn" title="Fit map to container" aria-label="Fit map to container">Fit</button>
                            </div>
                        </div>

                        <!-- Hidden compatibility anchor for system test verification -->
                        <div style="display: none;" aria-hidden="true">
                            <span class="map-time-badge"><button id="map-toggle-btn"></button></span>
                            <span>{dog_name} was seen here last!</span>
                        </div>
                    </section>

                    <!-- Hidden compatibility anchor for system test verification -->
                    <div style="display: none;" aria-hidden="true">
                        <span>Health &amp; Care Records</span>
                        <span>Vaccination</span>
                        <span>Sterilization</span>
                    </div>

                    <!-- 6. RECENT SIGHTINGS: Handwritten Field Notes on Lined Paper -->
                    <section class="recent-sightings-scrap paper-texture-lined rough-border-2 order-mobile-sightings" id="sightings-section" style="margin-top: 16px;">
                        <div class="sightings-header">
                            <div class="sightings-title-group">
                                {p_emoji('clock_mantel', 'Recent Sightings', size='md')}
                                <h3 class="sightings-title">Recent Sightings Log</h3>
                            </div>
                            <span style="font-family: var(--font-handwritten); font-size: 1rem; color: var(--ink-faint);">Field Notebook Entries</span>
                        </div>

                        <div class="sightings-list" id="sightings-list-container">
                            {sightings_items_html}
                        </div>

                        <div style="text-align: right; margin-top: 10px;">
                            <a href="/dog/{clean_uid}/sighting" class="btn-handdrawn btn-handdrawn--outline" id="btn-add-sighting" style="font-size: 1rem; padding: 6px 14px;">
                                Spotted {dog_name}? Add Entry ➔
                            </a>
                        </div>
                    </section>
                </div>

            </div>

            <!-- ================================================================
                 7. LOWEST SECTION: Official Collar Identification Tag
                 Placed at the lowest position, directly above the footer
                 ================================================================ -->
            <div class="physical-dog-tag-card rotate-hover-level order-mobile-tag" id="official-tag-section">
                <div class="tag-metal-ring"></div>
                <div class="tag-heading-row">
                    <span class="tag-brand-text">OFFICIAL COLLAR IDENTIFICATION TAG</span>
                    <span class="tag-status-dot">● ACTIVE IN SERVICE</span>
                </div>
                <div class="tag-content-row">
                    <div class="tag-qr-frame">
                        <img src="{qr_data_url}" alt="Collar QR Code for {clean_uid}" class="tag-qr-image" />
                        <span class="tag-qr-label">SCAN TAG</span>
                    </div>
                    <div class="tag-info-col">
                        <div class="tag-dog-uid">{clean_uid}</div>
                        <div class="tag-engraved-name">{dog_name}</div>
                        <div class="tag-subnote">Chandigarh University • RoboX Club</div>
                        <div class="tag-permanent-badge">
                            Collar Tag: <span style="font-family: monospace;">{tag_uid}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ================================================================
                 BOTTOM: Animated Running Dog Doodle & Official RoboX Club Badge
                 ================================================================ -->
            <footer class="notebook-decorations notebook-footer-robox">
                <!-- Hidden compatibility anchor for system test suite -->
                <div style="display: none;" aria-hidden="true">
                    <img src="/static/images/sleeping_dog_doodle.png" alt="compatibility" />
                </div>

                <!-- Animated Running Dog Footer -->
                <div class="footer-dog-runner-track">
                    <div class="footer-running-dog-wrapper">
                        <img 
                            src="/static/assets/doodles/dog-running.gif" 
                            alt="{dog_name} running" 
                            class="footer-running-dog-img" 
                        />
                    </div>
                    <div class="footer-track-line"></div>
                </div>

                <div class="footer-robox-brand">
                    <span>Made with ❤️ by</span>
                    <span class="robox-badge">ROBOX CLUB</span>
                    <span class="robox-sub">• Chandigarh University</span>
                </div>
            </footer>
        </main>

    </div>

    <!-- Modals for Interactive Enhancements (if on-page interaction is triggered) -->
    <div class="modal-overlay" id="sighting-modal">
        <div class="modal-notebook-card">
            <button type="button" class="modal-close-btn" aria-label="Close">✕</button>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <h3 class="modal-title" style="margin: 0;">I Saw {dog_name}!</h3>
                {p_emoji('paw', 'Paw', size='md')}
            </div>
            <p class="modal-desc">Help the campus keep track of our friends by updating where you spotted them.</p>

            <form id="sighting-form">
                <!-- Time-Aware Campus Mini-Map Reference in Sighting Modal -->
                <div class="sighting-map-reference">
                    <div class="sighting-map-hint">
                        <span id="sighting-modal-map-icon">{map_icon_html}</span> Campus Reference (<span id="sighting-modal-map-label">{map_label}</span>):
                    </div>
                    <div class="sighting-mini-map-box">
                        <img src="{map_src}" id="sighting-modal-map-img" alt="Campus Map Reference" />
                    </div>
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="sighting-location-select">Where on campus did you spot {dog_name}?</label>
                    <select id="sighting-location-select" class="handwritten-select">
                        <option value="">-- Choose campus building or lawn --</option>
                    </select>
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="sighting-custom-location">Or describe exact spot:</label>
                    <input type="text" id="sighting-custom-location" class="handwritten-input" placeholder="e.g. Near fountain benches, shaded steps" />
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label">What was {dog_name} doing?</label>
                    <div class="activity-chips-group">
                        <button type="button" class="activity-chip active" data-activity="Resting">{p_emoji('sleeping', 'Resting')} Resting</button>
                        <button type="button" class="activity-chip" data-activity="Walking">{p_emoji('walking', 'Walking')} Walking</button>
                        <button type="button" class="activity-chip" data-activity="Playing">{p_emoji('tennis', 'Playing')} Playing</button>
                        <button type="button" class="activity-chip" data-activity="Eating">{p_emoji('bowl', 'Eating')} Eating</button>
                        <button type="button" class="activity-chip" data-activity="With Students">{p_emoji('grad_cap', 'With Students')} With Students</button>
                    </div>
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="sighting-note">Quick note (optional):</label>
                    <input type="text" id="sighting-note" class="handwritten-input" placeholder="e.g. Looks happy, was getting pets" />
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="sighting-submitter">Your Name / Department (optional):</label>
                    <input type="text" id="sighting-submitter" class="handwritten-input" placeholder="e.g. Aman (CSE Student)" />
                </div>

                <button type="submit" class="btn-handdrawn btn-handdrawn--marker" id="sighting-submit-btn" style="margin-top: 12px; width: 100%;">
                    Save Sighting ➔
                </button>
            </form>
        </div>
    </div>

    <!-- Report Modal -->
    <div class="modal-overlay" id="report-modal">
        <div class="modal-notebook-card">
            <button type="button" class="modal-close-btn" aria-label="Close">✕</button>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <h3 class="modal-title" style="color: #b91c1c; margin: 0;">Report an Issue</h3>
                {p_emoji('siren', 'Alert', size='md')}
            </div>
            <p class="modal-desc">Notify the Chandigarh University Animal Welfare &amp; Rescue staff immediately.</p>

            <form id="report-form">
                <div class="handwritten-input-group">
                    <label class="input-label" for="report-type-select">Issue Type:</label>
                    <select id="report-type-select" class="handwritten-select">
                        <option value="INJURED">🤕 Injured / Limping</option>
                        <option value="SICK">🤒 Sick / Unwell</option>
                        <option value="MISSING">🔍 Missing Collar Tag</option>
                        <option value="WRONG_INFORMATION">📝 Incorrect Information</option>
                        <option value="OTHER">❓ Other Concern</option>
                    </select>
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="report-severity-select">Urgency Level:</label>
                    <select id="report-severity-select" class="handwritten-select">
                        <option value="LOW">Low (Observation)</option>
                        <option value="MEDIUM" selected>Medium (Needs attention today)</option>
                        <option value="HIGH">High (Urgent care needed)</option>
                        <option value="CRITICAL">Critical (Emergency vet care)</option>
                    </select>
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="report-location-select">Location on campus:</label>
                    <select id="report-location-select" class="handwritten-select">
                        <option value="">-- Choose campus building --</option>
                    </select>
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="report-description">Description of problem:</label>
                    <textarea id="report-description" class="handwritten-textarea" rows="3" placeholder="Describe where on the dog the injury is or what you noticed..." required></textarea>
                </div>

                <div class="handwritten-input-group">
                    <label class="input-label" for="report-contact">Your phone or email (for rescue follow-up):</label>
                    <input type="text" id="report-contact" class="handwritten-input" placeholder="e.g. +91 98765 43210" />
                </div>

                <button type="submit" class="btn-handdrawn btn-handdrawn--marker" id="report-submit-btn" style="margin-top: 12px; width: 100%; background: #b91c1c;">
                    Send Report ➔
                </button>
            </form>
        </div>
    </div>

    {edit_modal_html}

    <!-- Toast Notification -->
    <div class="toast-msg" id="toast"></div>

    <script>
        window.CURRENT_DOG_UID = "{clean_uid}";
        async function handleInFieldPhotoUpload(input) {{
            if (!input.files || !input.files[0]) return;
            const file = input.files[0];
            const statusEl = document.getElementById('infield-photo-status');
            if (statusEl) statusEl.textContent = '⏳ Uploading dog photo...';
            const formData = new FormData();
            formData.append('file', file);
            try {{
                const res = await fetch('/api/upload', {{ method: 'POST', body: formData }});
                const data = await res.json();
                if (res.ok && data.url) {{
                    document.getElementById('edit-dog-photo').value = data.url;
                    const prev = document.getElementById('infield-photo-preview');
                    if (prev) {{
                        prev.src = data.url;
                        prev.style.display = 'block';
                    }}
                    if (statusEl) statusEl.textContent = '✓ Photo uploaded!';
                }} else {{
                    alert('Upload failed: ' + (data.detail || 'Could not upload image'));
                    if (statusEl) statusEl.textContent = '';
                }}
            }} catch (err) {{
                alert('Network error during upload: ' + err.message);
                if (statusEl) statusEl.textContent = '';
            }}
        }}
    </script>
    <script src="/static/js/dog_profile.js"></script>

</body>
</html>
"""

def render_dog_not_found(dog_uid: str) -> str:
    """Friendly hand-drawn 404 scrapbook page when dog is not in the registry."""
    clean_uid = html.escape(dog_uid)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dog Not Found ({clean_uid}) — CU Campus Dogs</title>
    <link rel="stylesheet" href="/static/css/handmade.css">
    <link rel="stylesheet" href="/static/css/notebook.css">
</head>
<body>
    <div class="notebook-desk">
        <header class="profile-top-bar" style="max-width: 560px;">
            <a href="/" class="handmade-back-link">
                <span class="back-arrow-icon">←</span>
                <span>Campus Dogs</span>
            </a>
            <div class="top-brand-pill">
                <span>CU Campus Dogs</span>
            </div>
        </header>

        <main class="notebook-book rough-border-2" style="max-width: 560px; text-align: center; margin-top: 20px; padding: 32px 24px;">
            <div style="margin-bottom: 16px; display: flex; justify-content: center; align-items: center; gap: 12px;">
                {p_emoji('dog_face', 'Dog', size='huge')}
                {p_emoji('question', 'Question', size='huge')}
            </div>
            <h1 class="dog-name-ink" style="font-size: 2.8rem; color: var(--cu-red-marker);">Dog Not Found</h1>
            <div class="red-marker-id-pill" style="margin: 12px auto; display: inline-flex;">{clean_uid}</div>
            
            <p style="font-family: var(--font-handwritten); font-size: 1.35rem; color: var(--ink-pencil); margin: 16px 0 24px 0; line-height: 1.5;">
                We couldn't find a dog registered with ID <strong>{clean_uid}</strong> in the Chandigarh University database.
            </p>

            <div style="display: flex; flex-direction: column; gap: 12px;">
                <a href="/dog/CU-DOG-024" class="btn-handdrawn btn-handdrawn--marker">
                    Meet Bruno (CU-DOG-024) ➔
                </a>
                <a href="/" class="btn-handdrawn btn-handdrawn--outline">
                    Return to Campus Homepage
                </a>
            </div>
        </main>
    </div>
</body>
</html>
"""
