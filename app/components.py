import html
from datetime import datetime, timezone, timedelta
from typing import Optional

def render_button(
    label: str,
    variant: str = "marker", # 'marker' | 'kraft' | 'outline' | 'charcoal' | 'ghost'
    icon: Optional[str] = None, # 'camera' | 'warning' | 'pin' | 'share' | 'paw'
    href: Optional[str] = None,
    elem_id: Optional[str] = None,
    button_type: str = "button",
    class_name: str = "",
) -> str:
    """Renders a HandDrawnButton component."""
    id_attr = f'id="{html.escape(elem_id)}"' if elem_id else ""
    classes = f"btn-handdrawn btn-handdrawn--{variant} {class_name}".strip()

    icon_html = ""
    if icon == "camera":
        icon_html = """<span class="btn-handdrawn__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></span>"""
    elif icon == "warning":
        icon_html = '<span class="btn-handdrawn__icon">⚠️</span>'
    elif icon == "pin":
        icon_html = '<span class="btn-handdrawn__icon">📍</span>'
    elif icon == "share":
        icon_html = '<span class="btn-handdrawn__icon">🔗</span>'
    elif icon == "paw":
        icon_html = '<span class="btn-handdrawn__icon">🐾</span>'

    safe_label = html.escape(label)
    if href:
        return f'<a href="{html.escape(href)}" class="{classes}" {id_attr}>{icon_html}<span>{safe_label}</span></a>'
    return f'<button type="{button_type}" class="{classes}" {id_attr}>{icon_html}<span>{safe_label}</span></button>'


def render_paper_note(
    content: str,
    variant: str = "kraft", # 'kraft' | 'yellow' | 'cream' | 'lined' | 'grid'
    pin: str = "none",      # 'red' | 'tape' | 'paperclip' | 'none'
    rotate: float = 0,
    title: Optional[str] = None,
    class_name: str = "",
) -> str:
    """Renders a PaperNote component."""
    pin_html = ""
    if pin == "red":
        pin_html = '<div class="paper-note__pin-red"></div>'
    elif pin == "tape":
        pin_html = '<div class="paper-note__tape"></div>'
    elif pin == "paperclip":
        pin_html = '<img src="/static/assets/paper/paperclip.png" class="paper-note__paperclip" alt="clip" />'

    header_html = f'<div class="paper-note__header">{html.escape(title)}</div>' if title else ""
    rot_style = f"transform: rotate({rotate}deg);" if rotate != 0 else ""

    return f"""
    <div class="paper-note paper-note--{variant} {class_name}" style="{rot_style}">
        {pin_html}
        {header_html}
        <div class="paper-note__content">{content}</div>
    </div>
    """


def render_dog_photo(
    src: str = "/static/assets/dogs/bruno.png",
    alt: str = "Campus Dog",
    name: str = "",
    caption: Optional[str] = None,
    crown: bool = False,
    heart: bool = False,
    tape: str = "both", # 'both' | 'left' | 'right' | 'none'
    rotate: float = -1.5,
    tag_uid: Optional[str] = None,
) -> str:
    """Renders a DogPhoto polaroid component."""
    tape_left = '<div class="dog-photo__tape-left"></div>' if tape in ("both", "left") else ""
    tape_right = '<div class="dog-photo__tape-right"></div>' if tape in ("both", "right") else ""

    crown_html = """
    <svg class="dog-photo__crown" viewBox="0 0 100 60" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round">
        <path d="M10 50 L20 15 L45 35 L50 10 L55 35 L80 15 L90 50 Z" />
        <circle cx="20" cy="15" r="4" fill="#ffffff" />
        <circle cx="50" cy="10" r="4" fill="#ffffff" />
        <circle cx="80" cy="15" r="4" fill="#ffffff" />
    </svg>
    """ if crown else ""

    heart_html = """
    <svg class="dog-photo__heart" viewBox="0 0 24 24">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
    </svg>
    """ if heart else ""

    final_caption = caption or (f"Hey! I'm {name} :)" if name else "")
    caption_html = ""
    if final_caption:
        caption_html = f"""
        <div class="dog-photo__caption">
            <span>{html.escape(final_caption)}</span>
            <svg style="width: 40px; height: 20px; transform: rotate(-5deg);" viewBox="0 0 50 25" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                <path d="M5 20 Q 25 22, 42 8 M 35 6 L 45 7 L 42 16" />
            </svg>
        </div>
        """

    tag_html = ""
    if tag_uid:
        tag_html = f'<img src="/static/assets/tags/dog-tag.png" alt="Tag: {html.escape(tag_uid)}" style="position: absolute; bottom: -20px; right: -10px; width: 85px; filter: drop-shadow(2px 4px 4px rgba(0,0,0,0.25));" />'

    return f"""
    <div class="dog-photo-polaroid" style="transform: rotate({rotate}deg);">
        {tape_left}
        {tape_right}
        <div class="dog-photo__img-box">
            <img src="{html.escape(src)}" alt="{html.escape(alt)}" class="dog-photo__img" onerror="this.src='/static/assets/dogs/bruno.png'" />
            {crown_html}
            {heart_html}
        </div>
        {caption_html}
        {tag_html}
    </div>
    """


def render_dog_tag(
    dog_uid: str = "CU-DOG-024",
    variant: str = "pill", # 'pill' | 'collar' | 'red'
    tag_uid: Optional[str] = None,
) -> str:
    """Renders a DogTag component."""
    clean_uid = html.escape(dog_uid)
    if variant == "collar":
        return f"""
        <div class="dog-tag-collar" title="Dog ID: {clean_uid}">
            <img src="/static/assets/tags/dog-tag.png" alt="{clean_uid}" class="dog-tag-collar__img" />
        </div>
        """
    if variant == "red":
        return """
        <div class="dog-tag-collar" title="Chandigarh University Campus Dogs">
            <img src="/static/assets/tags/cu-red-tag.png" alt="CU Tag" class="dog-tag-collar__img" />
        </div>
        """
    return f'<span class="dog-tag-pill">{clean_uid}</span>'


def render_heading(
    text: str,
    level: int = 1,
    size: str = "xl", # 'sm' | 'md' | 'lg' | 'xl'
    sunburst: bool = False,
    underline: bool = False,
) -> str:
    """Renders a HandDrawnHeading component."""
    sunburst_html = """
    <svg class="heading-handdrawn__sunburst" viewBox="0 0 40 40">
        <line x1="20" y1="5" x2="20" y2="12" />
        <line x1="32" y1="9" x2="26" y2="15" />
        <line x1="35" y1="22" x2="28" y2="22" />
    </svg>
    """ if sunburst else ""

    underline_html = '<span class="heading-handdrawn__underline"></span>' if underline else ""

    return f"""
    <div style="position: relative; display: inline-block;">
        <h{level} class="heading-handdrawn heading-handdrawn--{size}">
            {html.escape(text)}
            {sunburst_html}
        </h{level}>
        {underline_html}
    </div>
    """


def render_doodle(
    name: str = "dog-sitting",
    width: str = "80px",
    rotate: float = 0,
    caption: Optional[str] = None,
) -> str:
    """Renders a Doodle component."""
    caption_html = f'<span class="doodle-caption">{html.escape(caption)}</span>' if caption else ""
    rot_style = f"transform: rotate({rotate}deg);" if rotate != 0 else ""
    clean_name = html.escape(name)

    return f"""
    <div class="doodle-wrapper" style="{rot_style}">
        <img src="/static/assets/doodles/{clean_name}.png" alt="{clean_name}" class="doodle-img" style="width: {width};" onerror="this.src='/static/assets/decorations/{clean_name}.png'" />
        {caption_html}
    </div>
    """


def render_location_note(
    location_name: str,
    time_ago: str = "Recently",
    activity: str = "Resting",
    map_src: Optional[str] = None,
    sticky_note: Optional[str] = None,
) -> str:
    """Renders a LocationNote component with time-aware Day/Night map support."""
    if not map_src:
        ist_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
        map_src = "/static/assets/maps/campus-map-day.png" if 8 <= ist_time.hour < 20 else "/static/assets/maps/campus-map-night.png"

    sticky_html = f'<div class="location-note-card__sticky">{html.escape(sticky_note)}</div>' if sticky_note else ""

    return f"""
    <div class="location-note-card">
        <div class="location-note-card__tape"></div>
        <div class="location-note-card__header">
            <div class="location-note-card__title">📍 Last Spotted</div>
            <span class="location-note-card__time">{html.escape(time_ago)}</span>
        </div>
        <div class="location-note-card__place">{html.escape(location_name)}</div>
        <div class="location-note-card__activity">Activity: {html.escape(activity)}</div>
        <div class="location-note-card__map-box">
            <img src="{html.escape(map_src)}" alt="{html.escape(location_name)}" class="location-note-card__map-img" />
            {sticky_html}
        </div>
    </div>
    """


def render_status_sticker(
    status: str = "active",
    label: Optional[str] = None,
    rotate: float = 0,
) -> str:
    """Renders a StatusSticker component."""
    norm = status.lower()
    default_label = label
    variant_class = "status-sticker--green"
    icon = "●"

    if norm == "registered":
        default_label = default_label or "✔ Registered Campus Dog"
        variant_class = "status-sticker--green"
        icon = ""
    elif norm == "active":
        default_label = default_label or "Active"
        variant_class = "status-sticker--green"
    elif norm == "vaccinated":
        default_label = default_label or "Vaccinated"
        variant_class = "status-sticker--green"
        icon = "💉"
    elif norm == "sterilized":
        default_label = default_label or "Sterilized"
        variant_class = "status-sticker--green"
        icon = "🐾"
    elif norm == "healthy":
        default_label = default_label or "Healthy"
        variant_class = "status-sticker--green"
        icon = "➕"
    elif norm in ("attention", "needs-care"):
        default_label = default_label or "Needs Attention"
        variant_class = "status-sticker--yellow"
        icon = "⚠️"
    elif norm in ("care", "injured"):
        default_label = default_label or "Under Treatment"
        variant_class = "status-sticker--red"
        icon = "🚨"
    elif norm == "good-boy":
        default_label = default_label or "Good Boy!"
        variant_class = "status-sticker--stamp"
        icon = "❤️"

    rot_style = f"transform: rotate({rotate}deg);" if rotate != 0 else ""
    icon_span = f"<span>{icon}</span>" if icon else ""

    return f"""
    <span class="status-sticker {variant_class}" style="{rot_style}">
        {icon_span}
        <span>{html.escape(default_label)}</span>
    </span>
    """


def render_divider(variant: str = "wavy-red") -> str:
    """Renders a HandDrawnDivider component."""
    if variant == "paw-trail":
        content = '<img src="/static/assets/decorations/divider-paw-trail.png" alt="paw trail" />'
    elif variant == "bone":
        content = '<img src="/static/assets/decorations/divider-bone.png" alt="bone divider" />'
    elif variant == "wavy-red":
        content = '<img src="/static/assets/decorations/divider-wavy-red.png" alt="wavy red divider" />'
    else:
        content = '<div class="handdrawn-divider--sketch-line" style="width: 100%;"></div>'

    return f'<div class="handdrawn-divider">{content}</div>'
