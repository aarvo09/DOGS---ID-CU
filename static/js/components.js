/**
 * CU Campus Dogs — Reusable Field Notebook Component Library
 * Standard Web Components & Custom Elements for modern HTML/browsers.
 * Compatible with Vanilla JS, React, Vue, or SSR templates.
 */

// 1. HandDrawnButton (<hand-drawn-button>)
class HandDrawnButton extends HTMLElement {
  connectedCallback() {
    const variant = this.getAttribute('variant') || 'marker';
    const href = this.getAttribute('href');
    const icon = this.getAttribute('icon');
    const type = this.getAttribute('type') || 'button';
    const id = this.getAttribute('id') ? `id="${this.getAttribute('id')}"` : '';
    const content = this.innerHTML;

    let iconHtml = '';
    if (icon === 'camera') {
      iconHtml = '<span class="btn-handdrawn__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></span>';
    } else if (icon === 'warning') {
      iconHtml = '<span class="btn-handdrawn__icon">⚠️</span>';
    } else if (icon === 'pin') {
      iconHtml = '<span class="btn-handdrawn__icon">📍</span>';
    } else if (icon === 'share') {
      iconHtml = '<span class="btn-handdrawn__icon">🔗</span>';
    } else if (icon === 'paw') {
      iconHtml = '<span class="btn-handdrawn__icon">🐾</span>';
    }

    if (href) {
      this.innerHTML = `<a href="${href}" class="btn-handdrawn btn-handdrawn--${variant}" ${id}>${iconHtml}<span>${content}</span></a>`;
    } else {
      this.innerHTML = `<button type="${type}" class="btn-handdrawn btn-handdrawn--${variant}" ${id}>${iconHtml}<span>${content}</span></button>`;
    }
  }
}
customElements.define('hand-drawn-button', HandDrawnButton);

// 2. PaperNote (<paper-note>)
class PaperNote extends HTMLElement {
  connectedCallback() {
    const variant = this.getAttribute('variant') || 'kraft';
    const pin = this.getAttribute('pin') || 'none';
    const rotate = this.getAttribute('rotate') || '0';
    const title = this.getAttribute('title');
    const content = this.innerHTML;

    let pinHtml = '';
    if (pin === 'red') pinHtml = '<div class="paper-note__pin-red"></div>';
    else if (pin === 'tape') pinHtml = '<div class="paper-note__tape"></div>';
    else if (pin === 'paperclip') pinHtml = '<img src="/static/assets/paper/paperclip.png" class="paper-note__paperclip" alt="clip" />';

    const headerHtml = title ? `<div class="paper-note__header">${title}</div>` : '';

    this.innerHTML = `
      <div class="paper-note paper-note--${variant}" style="transform: rotate(${rotate}deg);">
        ${pinHtml}
        ${headerHtml}
        <div class="paper-note__content">${content}</div>
      </div>
    `;
  }
}
customElements.define('paper-note', PaperNote);

// 3. DogPhoto (<dog-photo>)
class DogPhoto extends HTMLElement {
  connectedCallback() {
    const src = this.getAttribute('src') || '/static/assets/dogs/bruno.png';
    const alt = this.getAttribute('alt') || 'Campus Dog';
    const name = this.getAttribute('name') || '';
    const caption = this.getAttribute('caption') || (name ? `Hey! I'm ${name} :)` : '');
    const crown = this.getAttribute('crown') === 'true';
    const heart = this.getAttribute('heart') === 'true';
    const tape = this.getAttribute('tape') || 'both';
    const rotate = this.getAttribute('rotate') || '-1.5';
    const tagUid = this.getAttribute('tag-uid');

    const tapeLeftHtml = (tape === 'both' || tape === 'left') ? '<div class="dog-photo__tape-left"></div>' : '';
    const tapeRightHtml = (tape === 'both' || tape === 'right') ? '<div class="dog-photo__tape-right"></div>' : '';

    const crownHtml = crown ? `
      <svg class="dog-photo__crown" viewBox="0 0 100 60" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round">
        <path d="M10 50 L20 15 L45 35 L50 10 L55 35 L80 15 L90 50 Z" />
        <circle cx="20" cy="15" r="4" fill="#ffffff" />
        <circle cx="50" cy="10" r="4" fill="#ffffff" />
        <circle cx="80" cy="15" r="4" fill="#ffffff" />
      </svg>
    ` : '';

    const heartHtml = heart ? `
      <svg class="dog-photo__heart" viewBox="0 0 24 24">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      </svg>
    ` : '';

    const tagHtml = tagUid ? `
      <img src="/static/assets/tags/dog-tag.png" alt="Tag: ${tagUid}" class="hanging-collar-tag" style="position: absolute; bottom: -20px; right: -10px; width: 85px;" />
    ` : '';

    this.innerHTML = `
      <div class="dog-photo-polaroid" style="transform: rotate(${rotate}deg);">
        ${tapeLeftHtml}
        ${tapeRightHtml}
        <div class="dog-photo__img-box">
          <img src="${src}" alt="${alt}" class="dog-photo__img" onerror="this.src='/static/assets/dogs/bruno.png'" />
          ${crownHtml}
          ${heartHtml}
        </div>
        ${caption ? `<div class="dog-photo__caption">${caption}</div>` : ''}
        ${tagHtml}
      </div>
    `;
  }
}
customElements.define('dog-photo', DogPhoto);

// 4. DogTag (<dog-tag>)
class DogTag extends HTMLElement {
  connectedCallback() {
    const dogUid = this.getAttribute('dog-uid') || 'CU-DOG-024';
    const variant = this.getAttribute('variant') || 'pill';

    if (variant === 'collar') {
      this.innerHTML = `
        <div class="dog-tag-collar" title="Dog ID: ${dogUid}">
          <img src="/static/assets/tags/dog-tag.png" alt="${dogUid}" class="dog-tag-collar__img" />
        </div>
      `;
    } else if (variant === 'red') {
      this.innerHTML = `
        <div class="dog-tag-collar" title="CU Campus Dogs">
          <img src="/static/assets/tags/cu-red-tag.png" alt="CU Tag" class="dog-tag-collar__img" />
        </div>
      `;
    } else {
      // Default: Hand-drawn red marker ID pill
      this.innerHTML = `<span class="dog-tag-pill">${dogUid}</span>`;
    }
  }
}
customElements.define('dog-tag', DogTag);

// 5. HandDrawnHeading (<hand-drawn-heading>)
class HandDrawnHeading extends HTMLElement {
  connectedCallback() {
    const level = this.getAttribute('level') || '1';
    const size = this.getAttribute('size') || 'xl';
    const sunburst = this.getAttribute('sunburst') === 'true';
    const underline = this.getAttribute('underline') === 'true';
    const content = this.innerHTML;

    const sunburstHtml = sunburst ? `
      <svg class="heading-handdrawn__sunburst" viewBox="0 0 40 40">
        <line x1="20" y1="5" x2="20" y2="12" />
        <line x1="32" y1="9" x2="26" y2="15" />
        <line x1="35" y1="22" x2="28" y2="22" />
      </svg>
    ` : '';

    const underlineHtml = underline ? '<span class="heading-handdrawn__underline"></span>' : '';

    this.innerHTML = `
      <div style="position: relative; display: inline-block;">
        <h${level} class="heading-handdrawn heading-handdrawn--${size}">
          ${content}
          ${sunburstHtml}
        </h${level}>
        ${underlineHtml}
      </div>
    `;
  }
}
customElements.define('hand-drawn-heading', HandDrawnHeading);

// 6. Doodle (<doodle-asset>)
class DoodleAsset extends HTMLElement {
  connectedCallback() {
    const name = this.getAttribute('name') || 'dog-sitting';
    const width = this.getAttribute('width') || '80px';
    const rotate = this.getAttribute('rotate') || '0';
    const caption = this.getAttribute('caption');

    this.innerHTML = `
      <div class="doodle-wrapper" style="transform: rotate(${rotate}deg);">
        <img src="/static/assets/doodles/${name}.png" alt="${name}" class="doodle-img" style="width: ${width};" onerror="this.style.display='none'" />
        ${caption ? `<span class="doodle-caption">${caption}</span>` : ''}
      </div>
    `;
  }
}
customElements.define('doodle-asset', DoodleAsset);

// 7. LocationNote (<location-note>)
class LocationNote extends HTMLElement {
  connectedCallback() {
    const location = this.getAttribute('location') || 'Academic Block 2';
    const timeAgo = this.getAttribute('time-ago') || 'Recently';
    const activity = this.getAttribute('activity') || 'Resting';
    const mapSrc = this.getAttribute('map-src') || '/static/assets/maps/campus-map.png';
    const stickyNote = this.getAttribute('sticky-note') || 'Seen here last! :)';

    this.innerHTML = `
      <div class="location-note-card">
        <div class="location-note-card__tape"></div>
        <div class="location-note-card__header">
          <div class="location-note-card__title">📍 Last Spotted</div>
          <span class="location-note-card__time">${timeAgo}</span>
        </div>
        <div class="location-note-card__place">${location}</div>
        <div class="location-note-card__activity">Activity: ${activity}</div>
        <div class="location-note-card__map-box">
          <img src="${mapSrc}" alt="${location}" class="location-note-card__map-img" />
          <div class="location-note-card__sticky">${stickyNote}</div>
        </div>
      </div>
    `;
  }
}
customElements.define('location-note', LocationNote);

// 8. StatusSticker (<status-sticker>)
class StatusSticker extends HTMLElement {
  connectedCallback() {
    const status = (this.getAttribute('status') || 'active').toLowerCase();
    const customLabel = this.getAttribute('label');
    const rotate = this.getAttribute('rotate') || '0';

    let label = customLabel;
    let variantClass = 'status-sticker--green';
    let icon = '●';

    if (status === 'registered') {
      label = label || '✔ Registered Campus Dog';
      variantClass = 'status-sticker--green';
      icon = '';
    } else if (status === 'active') {
      label = label || 'Active';
      variantClass = 'status-sticker--green';
    } else if (status === 'vaccinated') {
      label = label || 'Vaccinated';
      variantClass = 'status-sticker--green';
      icon = '💉';
    } else if (status === 'sterilized') {
      label = label || 'Sterilized';
      variantClass = 'status-sticker--green';
      icon = '🐾';
    } else if (status === 'healthy') {
      label = label || 'Healthy';
      variantClass = 'status-sticker--green';
      icon = '➕';
    } else if (status === 'attention' || status === 'needs-care') {
      label = label || 'Needs Attention';
      variantClass = 'status-sticker--yellow';
      icon = '⚠️';
    } else if (status === 'injured' || status === 'care') {
      label = label || 'Under Treatment';
      variantClass = 'status-sticker--red';
      icon = '🚨';
    } else if (status === 'good-boy') {
      label = label || 'Good Boy!';
      variantClass = 'status-sticker--stamp';
      icon = '❤️';
    }

    this.innerHTML = `
      <span class="status-sticker ${variantClass}" style="transform: rotate(${rotate}deg);">
        ${icon ? `<span>${icon}</span>` : ''}
        <span>${label}</span>
      </span>
    `;
  }
}
customElements.define('status-sticker', StatusSticker);

// 9. HandDrawnDivider (<hand-drawn-divider>)
class HandDrawnDivider extends HTMLElement {
  connectedCallback() {
    const variant = this.getAttribute('variant') || 'wavy-red';
    let contentHtml = '';

    if (variant === 'paw-trail') {
      contentHtml = '<img src="/static/assets/decorations/divider-paw-trail.png" alt="paw trail" />';
    } else if (variant === 'bone') {
      contentHtml = '<img src="/static/assets/decorations/divider-bone.png" alt="bone divider" />';
    } else if (variant === 'wavy-red') {
      contentHtml = '<img src="/static/assets/decorations/divider-wavy-red.png" alt="wavy divider" />';
    } else {
      contentHtml = '<div class="handdrawn-divider--sketch-line" style="width: 100%;"></div>';
    }

    this.innerHTML = `<div class="handdrawn-divider">${contentHtml}</div>`;
  }
}
customElements.define('hand-drawn-divider', HandDrawnDivider);

console.log('🐾 CU Campus Dogs field notebook components initialized');
