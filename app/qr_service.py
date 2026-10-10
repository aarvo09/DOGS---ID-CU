import io
import base64
from typing import Optional
import qrcode
from qrcode.image.pil import PilImage
from app.config import BASE_URL

def get_tag_url(tag_uid: str, base_url: Optional[str] = None) -> str:
    """Returns the permanent canonical URL encoded inside the physical QR."""
    prefix = (base_url or BASE_URL).rstrip("/")
    return f"{prefix}/t/{tag_uid}"

def generate_qr_png_bytes(tag_uid: str, box_size: int = 10, border: int = 2, base_url: Optional[str] = None) -> bytes:
    """Generate PNG bytes of the QR code for a given tag_uid."""
    url = get_tag_url(tag_uid, base_url=base_url)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a1a", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def generate_artistic_qr_png_bytes(
    tag_uid: str,
    box_size: int = 12,
    border: int = 2,
    fill_color: str = "#991b1b",
    back_color: str = "#ffffff",
    with_center_paw: bool = True,
    base_url: Optional[str] = None
) -> bytes:
    """
    Generate high-resolution colorful artistic QR code PNG bytes with
    high error-correction (ERROR_CORRECT_H) and a hand-drawn center dog paw print.
    """
    from PIL import Image, ImageDraw

    url = get_tag_url(tag_uid, base_url=base_url)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    if with_center_paw:
        w, h = img.size
        # Sized ~21% of QR width, well within the 30% error correction budget
        center_size = int(w * 0.21)
        cx, cy = w // 2, h // 2
        box = (cx - center_size // 2, cy - center_size // 2, cx + center_size // 2, cy + center_size // 2)

        draw = ImageDraw.Draw(img)
        # Circular white badge with matching crimson border
        draw.ellipse(box, fill="#ffffff", outline=fill_color, width=max(2, int(center_size * 0.07)))

        # Hand-drawn paw print (pad + 3 toes)
        paw_r = center_size // 5.2
        # main pad
        draw.ellipse(
            (cx - paw_r * 1.15, cy - paw_r * 0.25, cx + paw_r * 1.15, cy + paw_r * 1.45),
            fill=fill_color
        )
        # left toe
        draw.ellipse(
            (cx - paw_r * 1.35, cy - paw_r * 1.15, cx - paw_r * 0.5, cy - paw_r * 0.35),
            fill=fill_color
        )
        # center toe
        draw.ellipse(
            (cx - paw_r * 0.42, cy - paw_r * 1.55, cx + paw_r * 0.42, cy - paw_r * 0.65),
            fill=fill_color
        )
        # right toe
        draw.ellipse(
            (cx + paw_r * 0.5, cy - paw_r * 1.15, cx + paw_r * 1.35, cy - paw_r * 0.35),
            fill=fill_color
        )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def generate_qr_data_url(tag_uid: str, box_size: int = 8) -> str:
    """Generate a base64 data URL representation of the QR code for instant UI embedding."""
    raw_bytes = generate_qr_png_bytes(tag_uid, box_size=box_size)
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def generate_artistic_qr_data_url(tag_uid: str, box_size: int = 10, fill_color: str = "#991b1b", base_url: Optional[str] = None) -> str:
    """Generate a base64 data URL representation of the artistic colorful QR code."""
    raw_bytes = generate_artistic_qr_png_bytes(tag_uid, box_size=box_size, fill_color=fill_color, base_url=base_url)
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def generate_printable_badge_html(tag_uid: str, dog_name: Optional[str] = None, dog_uid: Optional[str] = None) -> str:
    """
    Generate a high-resolution, printable collar tag HTML template with cutting guides,
    CU branding, tag identifier, and QR code.
    """
    data_url = generate_qr_data_url(tag_uid, box_size=12)
    tag_url = get_tag_url(tag_uid)

    dog_info_section = ""
    if dog_name and dog_uid:
        dog_info_section = f"""
        <div style="font-size: 13px; color: #4b5563; margin-top: 4px;">
            Assigned: <strong>{dog_name}</strong> ({dog_uid})
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Printable QR Collar Tag - {tag_uid}</title>
    <style>
        @media print {{
            body {{ margin: 0; background: white; }}
            .no-print {{ display: none; }}
            .badge-container {{ box-shadow: none !important; border: 2px dashed #9ca3af !important; }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #f3f4f6;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 20px;
        }}
        .badge-container {{
            background: #ffffff;
            width: 320px;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            text-align: center;
            border: 2px solid #e5e7eb;
            position: relative;
        }}
        .cu-badge-header {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 700;
            color: #b91c1c;
            margin-bottom: 2px;
        }}
        .cu-system-title {{
            font-size: 15px;
            font-weight: 800;
            color: #111827;
            margin-bottom: 16px;
        }}
        .qr-wrapper {{
            background: #ffffff;
            border: 1px solid #f3f4f6;
            border-radius: 12px;
            padding: 10px;
            display: inline-block;
            margin-bottom: 12px;
        }}
        .qr-image {{
            width: 200px;
            height: 200px;
            display: block;
        }}
        .tag-uid {{
            font-family: monospace;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 2px;
            color: #1f2937;
            background: #f9fafb;
            padding: 6px 14px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            display: inline-block;
            margin-bottom: 8px;
        }}
        .scan-instruction {{
            font-size: 12px;
            color: #6b7280;
            margin-top: 6px;
            line-height: 1.4;
        }}
        .tag-url {{
            font-size: 10px;
            color: #9ca3af;
            word-break: break-all;
            margin-top: 8px;
        }}
        .hole-punch {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2px dashed #9ca3af;
            margin: 0 auto 12px auto;
        }}
        .print-btn {{
            margin-bottom: 20px;
            padding: 10px 20px;
            background: #b91c1c;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(185, 28, 28, 0.3);
        }}
        .print-btn:hover {{
            background: #991b1b;
        }}
    </style>
</head>
<body>
    <button class="print-btn no-print" onclick="window.print()">🖨️ Print Physical Tag Badge</button>
    <div class="badge-container">
        <div class="hole-punch" title="Collar Hole Punch Guide"></div>
        <div class="cu-badge-header">Chandigarh University</div>
        <div class="cu-system-title">CAMPUS DOG IDENTITY TAG</div>
        
        <div class="qr-wrapper">
            <img class="qr-image" src="{data_url}" alt="Dog QR Code: {tag_uid}" />
        </div>
        
        <div>
            <div class="tag-uid">{tag_uid}</div>
        </div>

        {dog_info_section}

        <div class="scan-instruction">
            Scan with any smartphone camera to view identity or report location/injury.
        </div>
        <div class="tag-url">{tag_url}</div>
    </div>
</body>
</html>
"""


def get_default_tags_list(tags: list) -> list:
    """Helper to ensure exactly 10 tags are present."""
    default_fallbacks = [
        ("CU-TAG-8F42K9", "Bruno", "CU-DOG-024"),
        ("CU-TAG-9M31P2", "Milo", "CU-DOG-025"),
        ("CU-TAG-4K77X1", "Luna", "CU-DOG-026"),
        ("CU-TAG-SPAREE", None, None),
        ("CU-TAG-RBX101", None, None),
        ("CU-TAG-RBX102", None, None),
        ("CU-TAG-RBX103", None, None),
        ("CU-TAG-RBX104", None, None),
        ("CU-TAG-RBX105", None, None),
        ("CU-TAG-RBX106", None, None),
    ]
    working_tags = list(tags)
    existing_uids = {t.get("tag_uid") for t in working_tags if isinstance(t, dict)}
    for uid, dname, duid in default_fallbacks:
        if len(working_tags) >= 10:
            break
        if uid not in existing_uids:
            working_tags.append({
                "tag_uid": uid,
                "dog_name": dname,
                "dog_uid": duid,
                "status": "ACTIVE"
            })
            existing_uids.add(uid)
    return working_tags[:10]


def generate_printable_a4_sheet_html(tags: list, base_url: Optional[str] = None) -> str:
    """
    Generate a clean, downloadable A4 printable page with 10 dog collar QR codes.
    
    Strict requirements:
    - Pure printable A4 sheet, no website/UI/UX wrappers.
    - Each collar tag contains ONLY:
        1. 2cm x 2cm cartoonish QR code (crimson with central paw).
        2. 'SCAN ME'
        3. 'ROBO X'
    - Includes dashed scissors cutting borders and collar hole-punch circle.
    - Downloadable directly as PDF, PNG, or printed.
    """
    import html as html_module

    working_tags = get_default_tags_list(tags)

    tags_html = []
    for idx, t in enumerate(working_tags, start=1):
        tag_uid = html_module.escape(t.get("tag_uid", f"CU-TAG-RBX{idx:02d}"))
        qr_data_url = generate_artistic_qr_data_url(tag_uid, box_size=12, fill_color="#991b1b", base_url=base_url)

        tag_markup = f"""
        <div class="collar-tag">
            <span class="cut-scissors">✂</span>
            <div class="hole-punch" title="Collar Ring Hole Punch (Ø 4mm)"></div>
            <div class="qr-2cm-box" title="Exact 2cm x 2cm QR Code">
                <img src="{qr_data_url}" alt="QR Code" class="qr-img" />
            </div>
            <div class="scan-me-text">SCAN ME</div>
            <div class="robox-text">ROBO X</div>
        </div>
        """
        tags_html.append(tag_markup)

    all_tags_str = "\n".join(tags_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Printable Dog Collar Tags (10 QRs • 2cm × 2cm) — RoboX</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700;800&family=Nunito:wght@700;800;900&display=swap" rel="stylesheet">
    <style>
        /* ==========================================
           PRINT SETUP: Standard A4 Portrait
           ========================================== */
        @page {{
            size: A4 portrait;
            margin: 0;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background: #f1f5f9;
            font-family: 'Fredoka', 'Nunito', 'Comic Sans MS', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 24px 10px 40px 10px;
            color: #0f172a;
        }}

        /* ==========================================
           DOWNLOAD & PRINT TOOLBAR (Screen Only)
           ========================================== */
        .download-toolbar {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 20px;
            background: #ffffff;
            padding: 10px 20px;
            border-radius: 9999px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
            border: 1px solid #e2e8f0;
        }}

        .toolbar-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 9px 18px;
            border-radius: 9999px;
            font-family: 'Fredoka', 'Nunito', sans-serif;
            font-size: 14px;
            font-weight: 700;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .btn-pdf {{
            background: #991b1b;
            color: #ffffff;
        }}
        .btn-pdf:hover {{
            background: #7f1d1d;
            transform: translateY(-1px);
        }}

        .btn-png {{
            background: #0284c7;
            color: #ffffff;
        }}
        .btn-png:hover {{
            background: #0369a1;
            transform: translateY(-1px);
        }}

        .btn-print {{
            background: #0f172a;
            color: #ffffff;
        }}
        .btn-print:hover {{
            background: #1e293b;
            transform: translateY(-1px);
        }}

        /* ==========================================
           A4 SHEET CANVAS (210mm x 297mm)
           Contains 10 collar tags in a 2x5 grid
           ========================================== */
        .a4-page {{
            width: 210mm;
            height: 297mm;
            min-height: 297mm;
            max-height: 297mm;
            background: #ffffff;
            box-sizing: border-box;
            padding: 12mm 15mm;
            display: grid;
            grid-template-columns: repeat(2, 76mm);
            grid-template-rows: repeat(5, 49mm);
            gap: 6.5mm 18mm;
            justify-content: center;
            align-content: center;
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }}

        /* ==========================================
           INDIVIDUAL COLLAR TAG (76mm x 49mm)
           Contains ONLY:
           1. Hole Punch Guide (top)
           2. Exact 2cm x 2cm QR Code
           3. 'SCAN ME'
           4. 'ROBO X'
           ========================================== */
        .collar-tag {{
            width: 76mm;
            height: 49mm;
            box-sizing: border-box;
            background: #ffffff;
            border: 1.5px dashed #94a3b8;
            border-radius: 8px;
            padding: 3.5mm 4mm;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }}

        .cut-scissors {{
            position: absolute;
            top: 2mm;
            left: 2.5mm;
            font-size: 11px;
            color: #94a3b8;
            user-select: none;
            line-height: 1;
        }}

        .hole-punch {{
            width: 14px;
            height: 14px;
            border: 1.5px dashed #64748b;
            border-radius: 50%;
            margin: 0 auto 2.5mm auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .hole-punch::after {{
            content: '';
            width: 3.5px;
            height: 3.5px;
            background: #94a3b8;
            border-radius: 50%;
        }}

        /* EXACT REAL-LIFE 2CM X 2CM QR CODE */
        .qr-2cm-box {{
            width: 2cm;
            height: 2cm;
            min-width: 2cm;
            min-height: 2cm;
            max-width: 2cm;
            max-height: 2cm;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .qr-img {{
            width: 100%;
            height: 100%;
            display: block;
            object-fit: contain;
            image-rendering: -webkit-optimize-contrast;
            image-rendering: crisp-edges;
        }}

        /* 'SCAN ME' DIRECTLY UNDER QR */
        .scan-me-text {{
            font-family: 'Fredoka', 'Nunito', 'Comic Sans MS', sans-serif;
            font-size: 12px;
            font-weight: 800;
            color: #991b1b;
            letter-spacing: 0.8px;
            margin-top: 2.5mm;
            line-height: 1;
            text-transform: uppercase;
            text-align: center;
        }}

        /* 'ROBO X' DIRECTLY UNDER 'SCAN ME' */
        .robox-text {{
            font-family: 'Fredoka', 'Nunito', 'Comic Sans MS', sans-serif;
            font-size: 10.5px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: 1.2px;
            margin-top: 1.5mm;
            line-height: 1;
            text-transform: uppercase;
            text-align: center;
        }}

        /* ==========================================
           PRINT OVERRIDES (Strict Single Page A4)
           ========================================== */
        @media print {{
            body {{
                background: #ffffff !important;
                padding: 0 !important;
                margin: 0 !important;
            }}
            .no-print {{
                display: none !important;
            }}
            .a4-page {{
                box-shadow: none !important;
                border: none !important;
                width: 210mm !important;
                height: 297mm !important;
                padding: 12mm 15mm !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }}
            .collar-tag {{
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }}
        }}
    </style>
</head>
<body>

    <!-- DOWNLOAD & PRINT BAR (Screen Only) -->
    <div class="download-toolbar no-print">
        <a href="/print/robox-collar-tags.pdf{f'?base_url={base_url}' if base_url else ''}" class="toolbar-btn btn-pdf" download="robox-collar-tags-a4.pdf">
            📥 Download PDF
        </a>
        <a href="/print/robox-collar-tags.png{f'?base_url={base_url}' if base_url else ''}" class="toolbar-btn btn-png" download="robox-collar-tags-a4.png">
            🖼️ Download Image (PNG)
        </a>
        <button type="button" onclick="window.print()" class="toolbar-btn btn-print">
            🖨️ Print Sheet
        </button>
    </div>

    <!-- PURE A4 PRINTABLE SHEET (10 TAGS) -->
    <main class="a4-page">
        {all_tags_str}
    </main>

</body>
</html>
"""


def generate_printable_a4_sheet_pdf(tags: list, base_url: Optional[str] = None) -> bytes:
    """
    Generate an authentic print-ready A4 PDF document containing exactly 10
    collar tags, each with 2cm x 2cm QR code, 'SCAN ME', and 'ROBO X'.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm, mm
    from reportlab.lib.utils import ImageReader

    working_tags = get_default_tags_list(tags)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    page_w, page_h = A4

    tag_w = 76 * mm
    tag_h = 49 * mm
    cols = 2
    rows = 5

    margin_x = (page_w - (cols * tag_w)) / (cols + 1)
    gap_y = (page_h - 24 * mm - (rows * tag_h)) / (rows - 1)
    start_y = page_h - 12 * mm

    for idx, t in enumerate(working_tags[:10]):
        tag_uid = t.get("tag_uid", f"CU-TAG-RBX{idx+1:02d}")
        col = idx % 2
        row = idx // 2

        x = margin_x + col * (tag_w + margin_x)
        y = start_y - (row + 1) * tag_h - row * gap_y

        # Dashed scissors cutting boundary
        c.setDash(3, 3)
        c.setStrokeColorRGB(0.7, 0.73, 0.78)
        c.setLineWidth(0.8)
        c.roundRect(x, y, tag_w, tag_h, 3 * mm, stroke=1, fill=0)

        # Hole punch guide circle at top center
        c.setStrokeColorRGB(0.45, 0.5, 0.55)
        c.setDash(2, 2)
        c.circle(x + tag_w / 2, y + tag_h - 5.5 * mm, 2 * mm, stroke=1, fill=0)

        # 2cm x 2cm QR Code
        qr_bytes = generate_artistic_qr_png_bytes(tag_uid, box_size=12, fill_color="#991b1b", base_url=base_url)
        img_reader = ImageReader(io.BytesIO(qr_bytes))
        qr_x = x + (tag_w - 2 * cm) / 2
        qr_y = y + tag_h - 6.5 * mm - 2 * cm
        c.drawImage(img_reader, qr_x, qr_y, width=2 * cm, height=2 * cm)

        # SCAN ME text
        c.setDash()
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.6, 0.1, 0.1)  # Crimson
        text_y1 = qr_y - 4.5 * mm
        c.drawCentredString(x + tag_w / 2, text_y1, "SCAN ME")

        # ROBO X text
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColorRGB(0.06, 0.09, 0.16)  # Dark charcoal
        text_y2 = text_y1 - 3.8 * mm
        c.drawCentredString(x + tag_w / 2, text_y2, "ROBO X")

    c.showPage()
    c.save()
    return pdf_buffer.getvalue()


def generate_printable_a4_sheet_png(tags: list, base_url: Optional[str] = None) -> bytes:
    """
    Generate an authentic high-resolution 300 DPI A4 PNG image (2480 x 3508 px)
    containing the 10 collar tags with 2cm x 2cm QR codes, 'SCAN ME', and 'ROBO X'.
    """
    from PIL import Image, ImageDraw, ImageFont

    working_tags = get_default_tags_list(tags)

    dpi = 300
    page_w, page_h = 2480, 3508
    img = Image.new("RGB", (page_w, page_h), "#ffffff")
    draw = ImageDraw.Draw(img)

    tag_w = int((76.0 / 25.4) * dpi)
    tag_h = int((49.0 / 25.4) * dpi)
    qr_px = int((20.0 / 25.4) * dpi)

    cols, rows = 2, 5
    margin_x = (page_w - (cols * tag_w)) // (cols + 1)
    gap_y = (page_h - int((24.0 / 25.4) * dpi) - (rows * tag_h)) // (rows - 1)
    start_y = int((12.0 / 25.4) * dpi)

    try:
        font_scan = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_robox = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
    except:
        font_scan = ImageFont.load_default()
        font_robox = ImageFont.load_default()

    for idx, t in enumerate(working_tags[:10]):
        tag_uid = t.get("tag_uid", f"CU-TAG-RBX{idx+1:02d}")
        col = idx % 2
        row = idx // 2
        x = margin_x + col * (tag_w + margin_x)
        y = start_y + row * (tag_h + gap_y)

        # Tag border
        draw.rectangle([x, y, x + tag_w, y + tag_h], outline="#cbd5e1", width=3)

        # Hole punch guide circle
        hole_r = int((2.0 / 25.4) * dpi)
        hole_cx = x + tag_w // 2
        hole_cy = y + int((5.5 / 25.4) * dpi)
        draw.ellipse([hole_cx - hole_r, hole_cy - hole_r, hole_cx + hole_r, hole_cy + hole_r], outline="#94a3b8", width=2)

        # QR Code
        qr_bytes = generate_artistic_qr_png_bytes(tag_uid, box_size=12, fill_color="#991b1b", base_url=base_url)
        qr_pil = Image.open(io.BytesIO(qr_bytes)).convert("RGBA")
        qr_pil = qr_pil.resize((qr_px, qr_px), Image.ANTIALIAS)

        qr_x = x + (tag_w - qr_px) // 2
        qr_y = y + int((9.5 / 25.4) * dpi)
        img.paste(qr_pil, (qr_x, qr_y), qr_pil)

        # SCAN ME text
        scan_text = "SCAN ME"
        bbox1 = draw.textbbox((0, 0), scan_text, font=font_scan) if hasattr(draw, "textbbox") else (0, 0, 100, 30)
        tw1 = bbox1[2] - bbox1[0]
        th1 = bbox1[3] - bbox1[1]
        text_y1 = qr_y + qr_px + int((2.5 / 25.4) * dpi)
        draw.text((x + (tag_w - tw1) // 2, text_y1), scan_text, fill="#991b1b", font=font_scan)

        # ROBO X text
        robox_text = "ROBO X"
        bbox2 = draw.textbbox((0, 0), robox_text, font=font_robox) if hasattr(draw, "textbbox") else (0, 0, 80, 25)
        tw2 = bbox2[2] - bbox2[0]
        text_y2 = text_y1 + th1 + int((2.2 / 25.4) * dpi)
        draw.text((x + (tag_w - tw2) // 2, text_y2), robox_text, fill="#0f172a", font=font_robox)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
