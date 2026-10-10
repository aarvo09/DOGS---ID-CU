from app.components import (
    render_button,
    render_paper_note,
    render_dog_photo,
    render_dog_tag,
    render_heading,
    render_doodle,
    render_location_note,
    render_status_sticker,
    render_divider,
)

def render_component_showcase() -> str:
    """
    Renders an interactive workbench gallery showcasing all 9 core visual components
    and the organized asset library.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CU Campus Dogs — Field Notebook Component Showcase</title>
    <link rel="stylesheet" href="/static/css/handmade.css">
    <link rel="stylesheet" href="/static/css/notebook.css">
    <link rel="stylesheet" href="/static/css/components.css">
    <style>
        .showcase-container {{
            max-width: 1040px;
            width: 100%;
            margin: 20px auto;
        }}
        .showcase-section {{
            background: var(--paper-warm, #faf7ed);
            border: 2px solid var(--ink-black, #1f1b18);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 32px;
            box-shadow: 3px 4px 0 rgba(31, 27, 24, 0.85);
        }}
        .showcase-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: center;
            margin-top: 14px;
        }}
        .asset-card {{
            background: var(--paper-cream, #fffdf7);
            border: 1.5px solid var(--ink-black, #1f1b18);
            border-radius: 8px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            min-width: 130px;
            box-shadow: 1px 2px 0 rgba(0,0,0,0.15);
        }}
        .asset-label {{
            font-family: var(--font-hand, 'Patrick Hand', cursive);
            font-size: 0.95rem;
            color: var(--ink-pencil, #44403c);
        }}
        .code-snippet {{
            background: #1f1b18;
            color: #fef08a;
            font-family: monospace;
            font-size: 13px;
            padding: 10px 14px;
            border-radius: 6px;
            margin-top: 12px;
            overflow-x: auto;
        }}
        .token-swatches-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 14px;
            margin-top: 14px;
        }}
        .token-swatch {{
            border: var(--border-rough);
            border-radius: var(--radius-rough-1);
            background: var(--paper-cream);
            padding: 10px;
            box-shadow: var(--shadow-sketch-sm);
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .token-swatch__color {{
            height: 50px;
            border-radius: 6px;
            border: 1.5px solid var(--ink);
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.15);
        }}
        .token-swatch__name {{
            font-family: monospace;
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--ink);
        }}
        .token-swatch__hex {{
            font-family: var(--font-body);
            font-size: 0.8rem;
            color: var(--ink-muted);
        }}
        .handmade-effect-card {{
            background: var(--paper-cream);
            border: var(--border-rough);
            border-radius: 10px;
            padding: 18px;
            flex: 1 1 290px;
            box-shadow: var(--shadow-sketch-sm);
            display: flex;
            flex-direction: column;
            gap: 10px;
            position: relative;
        }}
        .handmade-effect-title {{
            font-family: var(--font-handwritten);
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--cu-red);
            border-bottom: 1.5px dashed var(--soft-gray-dark);
            padding-bottom: 4px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
    </style>
</head>
<body>
    <div class="showcase-container">

        <!-- Header -->
        <header style="margin-bottom: 24px; text-align: center;">
            <a href="/dog/CU-DOG-024" style="text-decoration: none;">
                {render_heading("CU Campus Dogs Component System", level=1, size="xl", sunburst=True, underline=True)}
            </a>
            <p style="font-family: var(--font-hand); font-size: 1.3rem; color: var(--ink-pencil); margin-top: 8px;">
                Reusable Hand-Drawn Field Notebook Component Library & Individual Asset System
            </p>
            <div style="margin-top: 12px;">
                <a href="/dog/CU-DOG-024" class="btn-handdrawn btn-handdrawn--marker">View Bruno Profile ➔</a>
            </div>
        </header>

        {render_divider("wavy-red")}

        <!-- ================================================================
             SECTION 0: CENTRALIZED DESIGN TOKENS
             ================================================================ -->
        <section class="showcase-section">
            {render_heading("Design Tokens: Colors, Typography & Spacing", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-body); font-size: 1rem; color: var(--ink-pencil); margin-top: 6px;">
                Single source of truth tokens defined in <code>static/css/handmade.css</code> ensuring aesthetic harmony across all campus dog interfaces.
            </p>

            <!-- COLORS -->
            <h3 style="font-family: var(--font-handwritten); font-size: 1.4rem; color: var(--cu-red); margin-top: 18px;">
                1. Centralized Color Tokens
            </h3>
            <div class="token-swatches-grid">
                <div class="token-swatch">
                    <div class="token-swatch__color" style="background: var(--cu-red);"></div>
                    <div class="token-swatch__name">--cu-red</div>
                    <div class="token-swatch__hex">#c41e3a (Identity)</div>
                </div>
                <div class="token-swatch">
                    <div class="token-swatch__color" style="background: var(--ink);"></div>
                    <div class="token-swatch__name">--ink</div>
                    <div class="token-swatch__hex">#1f1b18 (Charcoal)</div>
                </div>
                <div class="token-swatch">
                    <div class="token-swatch__color" style="background: var(--paper);"></div>
                    <div class="token-swatch__name">--paper</div>
                    <div class="token-swatch__hex">#faf7ed (Sketchbook)</div>
                </div>
                <div class="token-swatch">
                    <div class="token-swatch__color" style="background: var(--paper-dark);"></div>
                    <div class="token-swatch__name">--paper-dark</div>
                    <div class="token-swatch__hex">#ece6d8 (Kraft/Desk)</div>
                </div>
                <div class="token-swatch">
                    <div class="token-swatch__color" style="background: var(--muted-green);"></div>
                    <div class="token-swatch__name">--muted-green</div>
                    <div class="token-swatch__hex">#4d7c5f (Foliage)</div>
                </div>
                <div class="token-swatch">
                    <div class="token-swatch__color" style="background: var(--soft-gray);"></div>
                    <div class="token-swatch__name">--soft-gray</div>
                    <div class="token-swatch__hex">#e2ddd5 (Pencil)</div>
                </div>
            </div>

            <!-- TYPOGRAPHY -->
            <h3 style="font-family: var(--font-handwritten); font-size: 1.4rem; color: var(--cu-red); margin-top: 24px;">
                2. Typography System
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-top: 10px;">
                <div style="background: var(--paper-cream); border: var(--border-rough); border-radius: 8px; padding: 14px;">
                    <div style="font-family: monospace; font-size: 0.85rem; color: var(--cu-red); font-weight: 700;">
                        Functional Body Font (--font-body / --font-functional)
                    </div>
                    <div style="font-family: var(--font-body); font-size: 1.15rem; font-weight: 700; color: var(--ink); margin-top: 4px;">
                        Nunito (Clean, Legible Sans-Serif)
                    </div>
                    <p style="font-family: var(--font-body); font-size: 0.95rem; color: var(--ink-pencil); margin-top: 4px; line-height: 1.4;">
                        Engineered for dog IDs (<code>CU-DOG-024</code>), timestamps, telemetry, and administrative tables.
                    </p>
                </div>
                <div style="background: var(--paper-cream); border: var(--border-rough); border-radius: 8px; padding: 14px;">
                    <div style="font-family: monospace; font-size: 0.85rem; color: var(--cu-red); font-weight: 700;">
                        Handwritten &amp; Display Fonts (--font-display / --font-handwritten)
                    </div>
                    <div style="font-family: var(--font-display); font-size: 1.8rem; font-weight: 700; color: var(--ink); margin-top: 2px; line-height: 1.1;">
                        Caveat (Display &amp; Hero Titles)
                    </div>
                    <div style="font-family: var(--font-handwritten); font-size: 1.25rem; font-weight: 700; color: var(--ink-pencil); margin-top: 4px;">
                        Patrick Hand (Field Notebook UI &amp; Notes)
                    </div>
                    <div style="font-family: var(--font-annotation); font-size: 1.05rem; color: var(--cu-red); margin-top: 2px;">
                        Architects Daughter (Marginalia Annotations)
                    </div>
                </div>
            </div>

            <!-- SPACING -->
            <h3 style="font-family: var(--font-handwritten); font-size: 1.4rem; color: var(--cu-red); margin-top: 24px;">
                3. Consistent Spacing System (4px / 8px Scale)
            </h3>
            <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; margin-top: 10px; background: var(--paper-cream); padding: 14px; border: var(--border-rough); border-radius: 8px;">
                <div>
                    <div style="font-family: monospace; font-size: 0.75rem;">xs (8px)</div>
                    <div style="width: var(--space-xs); height: 28px; background: var(--cu-red-marker); border-radius: 2px; margin-top: 4px;"></div>
                </div>
                <div>
                    <div style="font-family: monospace; font-size: 0.75rem;">sm (12px)</div>
                    <div style="width: var(--space-sm); height: 28px; background: var(--cu-red-marker); border-radius: 2px; margin-top: 4px;"></div>
                </div>
                <div>
                    <div style="font-family: monospace; font-size: 0.75rem;">md (16px)</div>
                    <div style="width: var(--space-md); height: 28px; background: var(--cu-red-marker); border-radius: 2px; margin-top: 4px;"></div>
                </div>
                <div>
                    <div style="font-family: monospace; font-size: 0.75rem;">lg (24px)</div>
                    <div style="width: var(--space-lg); height: 28px; background: var(--cu-red-marker); border-radius: 2px; margin-top: 4px;"></div>
                </div>
                <div>
                    <div style="font-family: monospace; font-size: 0.75rem;">xl (32px)</div>
                    <div style="width: var(--space-xl); height: 28px; background: var(--cu-red-marker); border-radius: 2px; margin-top: 4px;"></div>
                </div>
                <div>
                    <div style="font-family: monospace; font-size: 0.75rem;">2xl (40px)</div>
                    <div style="width: var(--space-2xl); height: 28px; background: var(--cu-red-marker); border-radius: 2px; margin-top: 4px;"></div>
                </div>
                <div>
                    <div style="font-family: monospace; font-size: 0.75rem;">3xl (48px)</div>
                    <div style="width: var(--space-3xl); height: 28px; background: var(--cu-red-marker); border-radius: 2px; margin-top: 4px;"></div>
                </div>
            </div>
        </section>

        <!-- ================================================================
             SECTION 0B: THE 10 HANDMADE EFFECT UTILITIES (CONTROLLED IMPERFECTION)
             ================================================================ -->
        <section class="showcase-section">
            {render_heading("The 10 Handmade Effect Utilities", level=2, size="lg", sunburst=True, underline=True)}
            <p style="font-family: var(--font-body); font-size: 1rem; color: var(--ink-pencil); margin-top: 6px;">
                Reusable CSS classes and utilities designed with <strong>controlled imperfection</strong> — authentic character without visual chaos.
            </p>

            <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-top: 18px;">

                <!-- 1. Rough Borders -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>1. Rough Borders</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.rough-border</code>
                    </div>
                    <div class="rough-border" style="padding: 12px; background: var(--paper);">
                        Default 2px rough wobbly outline.
                    </div>
                    <div class="rough-border-thick" style="padding: 12px; background: var(--paper-kraft);">
                        Thick 3px organic sketch border.
                    </div>
                    <div class="rough-border-dashed" style="padding: 10px; background: var(--paper);">
                        Hand-dashed ink perimeter.
                    </div>
                </div>

                <!-- 2. Marker Underline -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>2. Marker Underline</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.marker-underline</code>
                    </div>
                    <div style="font-family: var(--font-handwritten); font-size: 1.3rem; line-height: 1.8;">
                        <span class="marker-underline marker-underline--red">Red marker emphasis</span><br>
                        <span class="marker-underline marker-underline--yellow">Sunny yellow underline</span><br>
                        <span class="marker-underline marker-underline--green">Field green highlighter</span><br>
                        <span class="marker-underline-wavy">Wavy hand-drawn line</span>
                    </div>
                </div>

                <!-- 3. Paper Texture -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>3. Paper Texture</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.paper-texture</code>
                    </div>
                    <div class="paper-texture rough-border-thin" style="padding: 10px; font-family: var(--font-body); font-size: 0.85rem;">
                        <strong>Sketchbook Grain:</strong> subtle fiber stippling.
                    </div>
                    <div class="paper-texture-grid rough-border-thin" style="padding: 10px; font-family: var(--font-body); font-size: 0.85rem;">
                        <strong>Grid Texture:</strong> 16px notebook graph paper.
                    </div>
                    <div class="paper-texture-lined rough-border-thin" style="padding: 8px 10px; font-family: var(--font-annotation); font-size: 0.95rem;">
                        Ruled notebook paper line structure.
                    </div>
                </div>

                <!-- 4. Torn-Paper Edge -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>4. Torn-Paper Edge</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.torn-edge-bottom</code>
                    </div>
                    <div class="torn-edge-bottom rough-border" style="background: var(--paper-cream); padding: 14px; font-family: var(--font-handwritten); font-size: 1.1rem;">
                        Notebook page with micro-jagged bottom tear rip!
                    </div>
                    <div class="torn-edge-top rough-border" style="background: var(--paper-kraft); padding: 14px; font-family: var(--font-handwritten); font-size: 1.1rem; margin-top: 4px;">
                        Torn top edge paper slip.
                    </div>
                </div>

                <!-- 5. Slight Rotation (Controlled Imperfection) -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>5. Slight Rotation</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.rotate-slight-*</code>
                    </div>
                    <p style="font-family: var(--font-body); font-size: 0.85rem; color: var(--ink-muted);">
                        Controlled micro-angles (0.6° to 1.5°). Levels on hover:
                    </p>
                    <div style="display: flex; gap: 10px; justify-content: center; margin-top: 6px;">
                        <div class="rotate-slight-left rotate-hover-level rough-border" style="padding: 8px 12px; background: var(--paper-yellow); font-family: var(--font-handwritten); cursor: pointer;">
                            -1.2° (Hover me)
                        </div>
                        <div class="rotate-slight-right rotate-hover-level rough-border" style="padding: 8px 12px; background: var(--paper-cream); font-family: var(--font-handwritten); cursor: pointer;">
                            +1.2° (Hover me)
                        </div>
                    </div>
                </div>

                <!-- 6. Tape Effect -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>6. Tape Effect</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.tape-strip / .has-tape-*</code>
                    </div>
                    <div class="has-tape-top rough-border" style="background: var(--paper-cream); padding: 22px 14px 12px 14px; margin-top: 10px; text-align: center; font-family: var(--font-handwritten);">
                        Pinned with top washi tape strip
                    </div>
                    <div class="has-tape-corners rough-border" style="background: var(--paper); padding: 18px 14px 12px 14px; margin-top: 8px; text-align: center; font-family: var(--font-handwritten);">
                        Dual corner washi tape fasteners
                    </div>
                </div>

                <!-- 7. Handwritten Annotation -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>7. Handwritten Annotation</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.handwritten-annotation</code>
                    </div>
                    <div class="handwritten-annotation annotation-red">
                        <svg class="annotation-arrow" viewBox="0 0 24 16"><path d="M2 14 Q10 2 22 8 M16 4 L22 8 L18 14"/></svg>
                        Student Field Note: "Friendly with snacks!"
                    </div>
                    <div class="handwritten-annotation annotation-pencil" style="margin-top: 8px;">
                        Graphite note: Verified by Animal Welfare Club
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="annotation-badge">🏷️ CU-DOG-024</span>
                    </div>
                </div>

                <!-- 8. Sketch Shadow -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>8. Sketch Shadow</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.sketch-shadow-*</code>
                    </div>
                    <div class="sketch-shadow-press rough-border" style="background: var(--paper-cream); padding: 10px 14px; font-family: var(--font-handwritten); font-size: 1.1rem; text-align: center;">
                        Charcoal Shadow (Click / Press me)
                    </div>
                    <div class="sketch-shadow-double rough-border" style="background: var(--paper-kraft); padding: 10px 14px; font-family: var(--font-handwritten); font-size: 1.1rem; text-align: center; margin-top: 8px;">
                        Double-Layered Sketch Shadow
                    </div>
                </div>

                <!-- 9. Imperfect Circle -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>9. Imperfect Circle</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.imperfect-circle</code>
                    </div>
                    <div style="display: flex; gap: 12px; align-items: center; justify-content: center; margin-top: 6px;">
                        <div class="imperfect-circle">CU</div>
                        <div class="imperfect-circle imperfect-circle--red imperfect-circle--wobbly">024</div>
                        <div class="imperfect-circle imperfect-circle--double">🐾</div>
                        <span class="circle-highlight" style="font-family: var(--font-handwritten); font-weight: 700;">Circled!</span>
                    </div>
                </div>

                <!-- 10. Marker Highlight -->
                <div class="handmade-effect-card">
                    <div class="handmade-effect-title">
                        <span>10. Marker Highlight</span>
                        <code style="font-size: 0.8rem; color: var(--ink);">.marker-highlight</code>
                    </div>
                    <p style="font-family: var(--font-body); font-size: 0.95rem; line-height: 1.8; color: var(--ink);">
                        Bruno is <span class="marker-highlight marker-highlight--yellow">Chandigarh University's</span> campus mascot. 
                        He is <span class="marker-highlight marker-highlight--green">fully vaccinated</span> and carries collar tag 
                        <span class="marker-highlight marker-highlight--red">CU-TAG-8F42K9</span>.
                    </p>
                </div>

            </div>
        </section>

        {render_divider("wavy-red")}

        <!-- 1. HandDrawnButton -->
        <section class="showcase-section">
            {render_heading("1. HandDrawnButton", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Marker stroke, kraft paper, outline, charcoal brush, and wavy ghost button variants with tactile press effects.
            </p>
            <div class="showcase-grid">
                {render_button("I SAW THIS DOG ➔", variant="marker", icon="camera")}
                {render_button("REPORT AN ISSUE ➔", variant="kraft", icon="warning")}
                {render_button("View Last Location", variant="outline", icon="pin")}
                {render_button("Share Dog Profile", variant="outline", icon="share")}
                {render_button("SUBMIT SIGHTING ➔", variant="charcoal")}
                {render_button("View All Sightings ➔", variant="ghost")}
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;hand-drawn-button variant="marker" icon="camera"&gt;I SAW THIS DOG ➔&lt;/hand-drawn-button&gt;<br><br>
                // React Component<br>
                &lt;HandDrawnButton variant="marker" icon="camera"&gt;I SAW THIS DOG ➔&lt;/HandDrawnButton&gt;
            </div>
        </section>

        <!-- 2. PaperNote -->
        <section class="showcase-section">
            {render_heading("2. PaperNote", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Torn paper notes in kraft cardboard, yellow sticky, cream sketchbook, lined notebook, and grid paper textures.
            </p>
            <div class="showcase-grid" style="align-items: stretch;">
                <div style="flex: 1; min-width: 200px;">
                    {render_paper_note("Beloved indie dog near Block 2. Extremely friendly and loves students!", variant="kraft", pin="red", title="Personality Note", rotate=-1)}
                </div>
                <div style="flex: 1; min-width: 200px;">
                    {render_paper_note("Bruno was seen near the central lawn fountain 14m ago!", variant="yellow", pin="tape", title="Field Memo", rotate=1.5)}
                </div>
                <div style="flex: 1; min-width: 200px;">
                    {render_paper_note("Vaccinated for Rabies + DHPPiL. Microchipped collar band applied.", variant="lined", pin="paperclip", title="Vet Health Note", rotate=-0.5)}
                </div>
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;paper-note variant="kraft" pin="red" title="Personality Note"&gt;Content here...&lt;/paper-note&gt;
            </div>
        </section>

        <!-- 3. DogPhoto -->
        <section class="showcase-section">
            {render_heading("3. DogPhoto", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Polaroid scrapbook frame with washi tape, crown and heart doodles, and hanging metal QR collar tag.
            </p>
            <div class="showcase-grid" style="justify-content: center; gap: 32px;">
                {render_dog_photo(src="/static/assets/dogs/bruno.png", name="Bruno", crown=True, heart=True, tag_uid="CU-DOG-024", rotate=-2)}
                {render_dog_photo(src="/static/assets/dogs/milo.png", name="Milo", crown=False, heart=True, tag_uid="CU-DOG-025", rotate=1.5)}
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;dog-photo src="/static/assets/dogs/bruno.png" name="Bruno" crown="true" heart="true" tag-uid="CU-DOG-024"&gt;&lt;/dog-photo&gt;
            </div>
        </section>

        <!-- 4. DogTag -->
        <section class="showcase-section">
            {render_heading("4. DogTag", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Physical identity collar tags: silver QR dog tag, red enamel CU Campus Dogs tag, and hand-drawn red marker pill.
            </p>
            <div class="showcase-grid">
                <div class="asset-card">
                    {render_dog_tag("CU-DOG-024", variant="collar")}
                    <span class="asset-label">Collar Tag (QR)</span>
                </div>
                <div class="asset-card">
                    {render_dog_tag("CU-DOG-024", variant="red")}
                    <span class="asset-label">Enamel CU Tag</span>
                </div>
                <div class="asset-card">
                    {render_dog_tag("CU-DOG-024", variant="pill")}
                    <span class="asset-label">Marker ID Pill</span>
                </div>
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;dog-tag dog-uid="CU-DOG-024" variant="collar"&gt;&lt;/dog-tag&gt;
            </div>
        </section>

        <!-- 5. HandDrawnHeading -->
        <section class="showcase-section">
            {render_heading("5. HandDrawnHeading", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Ink brush lettering with red marker sunburst dashes and hand-drawn underline strokes.
            </p>
            <div style="display: flex; flex-direction: column; gap: 16px; margin-top: 14px;">
                {render_heading("Bruno", level=1, size="xl", sunburst=True)}
                {render_heading("Health & Care Dossier", level=2, size="lg", underline=True)}
                {render_heading("Recent Sightings Log", level=3, size="md", underline=True)}
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;hand-drawn-heading level="1" size="xl" sunburst="true"&gt;Bruno&lt;/hand-drawn-heading&gt;
            </div>
        </section>

        <!-- 6. Doodle -->
        <section class="showcase-section">
            {render_heading("6. Doodle", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Individually isolated doodle illustrations for campus dog behaviors, marginalia, and campus landmarks.
            </p>
            <div class="showcase-grid">
                <div class="asset-card">
                    {render_doodle("dog-sitting", width="70px", caption="dog-sitting")}
                </div>
                <div class="asset-card">
                    {render_doodle("dog-sleeping", width="85px", caption="dog-sleeping")}
                </div>
                <div class="asset-card">
                    {render_doodle("dog-running", width="85px", caption="dog-running")}
                </div>
                <div class="asset-card">
                    {render_doodle("dog-peeking", width="65px", caption="dog-peeking")}
                </div>
                <div class="asset-card">
                    {render_doodle("cu-building", width="75px", caption="cu-building")}
                </div>
                <div class="asset-card">
                    {render_doodle("tree-doodle", width="50px", caption="tree-doodle")}
                </div>
                <div class="asset-card">
                    {render_doodle("bone", width="45px", caption="bone")}
                </div>
                <div class="asset-card">
                    {render_doodle("star", width="40px", caption="star")}
                </div>
                <div class="asset-card">
                    {render_doodle("crown", width="45px", caption="crown")}
                </div>
                <div class="asset-card">
                    {render_doodle("arrow-red", width="60px", caption="arrow-red")}
                </div>
                <div class="asset-card">
                    {render_doodle("speech-bubble", width="85px", caption="speech-bubble")}
                </div>
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;doodle-asset name="dog-sitting" width="70px" caption="Sitting pup"&gt;&lt;/doodle-asset&gt;
            </div>
        </section>

        <!-- 7. LocationNote -->
        <section class="showcase-section">
            {render_heading("7. LocationNote", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Illustrated Chandigarh University campus map card with dynamic time-aware switching:
                <strong>Daytime View</strong> (8:00 AM – 8:00 PM: Day View Map) and <strong>Nighttime View</strong> (8:00 PM – 8:00 AM: Night-Time Map with Lights).
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 24px; margin-top: 14px;">
                <div>
                    <div style="font-family: var(--font-hand); font-weight: 700; font-size: 1.1rem; color: #b45309; margin-bottom: 8px;">
                        ☀️ Daytime View (8:00 AM – 8:00 PM)
                    </div>
                    {render_location_note("Academic Block 2 (Computing & AI)", time_ago="12 minutes ago", activity="Resting", map_src="/static/assets/maps/campus-map-day.png", sticky_note="Bruno was seen here last! :)")}
                </div>
                <div>
                    <div style="font-family: var(--font-hand); font-weight: 700; font-size: 1.1rem; color: #1e3a8a; margin-bottom: 8px;">
                        🌙 Nighttime View (8:00 PM – 8:00 AM)
                    </div>
                    {render_location_note("Central Lawn (Near Fountain)", time_ago="35 minutes ago", activity="Night patrol 🐾", map_src="/static/assets/maps/campus-map-night.png", sticky_note="Night-time lights map!")}
                </div>
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component: Defaults automatically to Day or Night map based on time --&gt;<br>
                &lt;location-note location="Academic Block 2" time-ago="12m ago" activity="Resting" sticky-note="Bruno was here!"&gt;&lt;/location-note&gt;
            </div>
        </section>

        <!-- 8. StatusSticker -->
        <section class="showcase-section">
            {render_heading("8. StatusSticker", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Hand-drawn torn paper status badges and stamps for health, vaccination, and registration status.
            </p>
            <div class="showcase-grid">
                {render_status_sticker("registered")}
                {render_status_sticker("active")}
                {render_status_sticker("vaccinated")}
                {render_status_sticker("sterilized")}
                {render_status_sticker("healthy")}
                {render_status_sticker("attention")}
                {render_status_sticker("care")}
                {render_status_sticker("good-boy")}
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;status-sticker status="registered"&gt;&lt;/status-sticker&gt;<br>
                &lt;status-sticker status="vaccinated"&gt;&lt;/status-sticker&gt;
            </div>
        </section>

        <!-- 9. HandDrawnDivider -->
        <section class="showcase-section">
            {render_heading("9. HandDrawnDivider", level=2, size="lg", sunburst=False, underline=True)}
            <p style="font-family: var(--font-hand); font-size: 1.15rem; color: var(--ink-pencil);">
                Hand-drawn wavy red marker lines, paw trails, and bone divider graphics.
            </p>
            <div style="margin-top: 16px;">
                <p class="asset-label">Wavy Red Marker:</p>
                {render_divider("wavy-red")}
                <p class="asset-label">Paw Trail:</p>
                {render_divider("paw-trail")}
                <p class="asset-label">Bone Divider:</p>
                {render_divider("bone")}
                <p class="asset-label">Sketch Pencil Line:</p>
                {render_divider("sketch")}
            </div>
            <div class="code-snippet">
                &lt;!-- HTML / Web Component --&gt;<br>
                &lt;hand-drawn-divider variant="wavy-red"&gt;&lt;/hand-drawn-divider&gt;<br>
                &lt;hand-drawn-divider variant="paw-trail"&gt;&lt;/hand-drawn-divider&gt;
            </div>
        </section>

    </div>

    <script src="/static/components/index.js"></script>
</body>
</html>
"""
