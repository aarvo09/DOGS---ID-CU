/**
 * CU Campus Dogs — Field Notebook Interactive Controller
 * Handles live profile synchronization, community sightings, reporting,
 * copy link / sharing, and interactive doodle animations.
 */

(function () {
  'use strict';

  // State
  let currentDogUid = window.CURRENT_DOG_UID || 'CU-DOG-024';
  let currentDogData = null;
  let activeActivity = 'Resting';

  // Elements
  const toastEl = document.getElementById('toast');
  const sightingModal = document.getElementById('sighting-modal');
  const reportModal = document.getElementById('report-modal');

  function pEmoji(name, alt = '', size = '') {
    const sizeCls = size ? ` premium-emoji--${size}` : '';
    return `<img src="/static/assets/emojis/${name}.webp" class="premium-emoji${sizeCls}" alt="${alt}" draggable="false" />`;
  }

  function showToast(message) {
    if (!toastEl) return;
    toastEl.innerHTML = message;
    toastEl.classList.add('show');
    setTimeout(() => {
      toastEl.classList.remove('show');
    }, 3200);
  }

  // Fetch Dog Profile Details from API
  async function loadDogProfile() {
    try {
      const res = await fetch(`/api/dogs/${encodeURIComponent(currentDogUid)}`);
      if (!res.ok) {
        throw new Error(`Profile fetch failed: ${res.status}`);
      }
      const data = await res.json();
      currentDogData = data;
      renderDogDetails(data);
    } catch (err) {
      console.warn('Using pre-rendered server state:', err);
    }
  }

  // Fetch Sightings List
  async function loadSightings() {
    try {
      const res = await fetch(`/api/dogs/${encodeURIComponent(currentDogUid)}/sightings?limit=5`);
      if (!res.ok) return;
      const sightings = await res.json();
      renderSightingsList(sightings);
    } catch (err) {
      console.warn('Could not refresh sightings:', err);
    }
  }

  // Fetch Campus Locations for dropdown
  async function loadCampusLocations() {
    try {
      const res = await fetch('/api/locations');
      if (!res.ok) return;
      const locations = await res.json();
      populateLocationDropdowns(locations);
    } catch (err) {
      console.warn('Could not load campus locations:', err);
    }
  }

  function canonicalCampusLocation(locName) {
    const s = (locName || '').trim().toLowerCase();
    if (s.includes('park') || s.includes('gate') || s.includes('car') || s.includes('vehicle')) return 'Parking';
    if (s.includes('block f') || s.includes('block 3') || s.includes('management')) return 'Academic Block F';
    if (s.includes('block e') || s.includes('block 2') || s.includes('computing') || s.includes('ai') || s.includes('quad')) return 'Academic Block E';
    if (s.includes('hostel b') || s.includes('south') || s.includes('girl')) return 'Hostel B';
    if (s.includes('hostel a') || s.includes('hostel') || s.includes('block a') || s.includes('block 1') || s.includes('engineering') || s.includes('north') || s.includes('boy')) return 'Hostel A';
    if (s.includes('field') || s.includes('ground') || s.includes('sports') || s.includes('cricket') || s.includes('stadium')) return 'Field';
    if (s.includes('pond') || s.includes('lake') || s.includes('lawn') || s.includes('fountain') || s.includes('water') || s.includes('central')) return 'Pond';
    return 'Academic Block E';
  }

  function renderDogDetails(dog) {
    // Update Name & ID
    const nameEl = document.getElementById('dog-name-display');
    if (nameEl) nameEl.textContent = dog.name;

    const idEl = document.getElementById('dog-id-display');
    if (idEl) idEl.textContent = dog.dog_uid;

    // Update Photo if provided
    const photoEl = document.getElementById('dog-photo-img');
    if (photoEl && dog.photo_url) {
      photoEl.src = dog.photo_url;
    }

    // Update Last Seen info (normalized to canonical names)
    if (dog.last_seen) {
      const cleanLoc = canonicalCampusLocation(dog.last_seen.location);
      const placeEl = document.getElementById('spotted-place-display');
      if (placeEl) placeEl.textContent = cleanLoc;

      const timeEl = document.getElementById('spotted-time-display');
      if (timeEl) timeEl.textContent = dog.last_seen.time_ago || 'Recently';

      const actEl = document.getElementById('spotted-activity-display');
      if (actEl) {
        actEl.textContent = `Activity: ${dog.last_seen.activity || 'Spotted on campus'}`;
      }

      // Update map pin coordinates and tooltip dynamically
      const pinCoords = {
        'Parking': { x: 7.2, y: 25.9 },
        'Academic Block F': { x: 34.8, y: 13.7 },
        'Academic Block E': { x: 37.1, y: 35.6 },
        'Field': { x: 36.5, y: 61.0 },
        'Pond': { x: 67.7, y: 59.6 },
        'Hostel A': { x: 36.5, y: 81.1 },
        'Hostel B': { x: 69.0, y: 81.1 },
      };
      const pinEl = document.getElementById('map-dog-pin');
      if (pinEl && pinCoords[cleanLoc]) {
        pinEl.style.left = `${pinCoords[cleanLoc].x}%`;
        pinEl.style.top = `${pinCoords[cleanLoc].y}%`;
        const tipEl = pinEl.querySelector('.map-pin-tooltip');
        if (tipEl) tipEl.textContent = `${dog.name || 'Dog'} spotted here`;
      }
    }

    // Update Health
    if (dog.health_overview) {
      const hStatusEl = document.getElementById('health-status-badge');
      if (hStatusEl) {
        hStatusEl.textContent = dog.health_overview.health_status || 'Healthy';
      }
      const vStatusEl = document.getElementById('vacc-status-badge');
      if (vStatusEl) {
        vStatusEl.textContent = (dog.health_overview.vaccination_status === 'UP_TO_DATE' ? 'Up to date' : dog.health_overview.vaccination_status);
      }
      const sStatusEl = document.getElementById('ster-status-badge');
      if (sStatusEl) {
        sStatusEl.textContent = (dog.health_overview.sterilization_status === 'STERILIZED' ? 'Yes' : dog.health_overview.sterilization_status);
      }
    }
  }

  function renderSightingsList(sightings) {
    const listEl = document.getElementById('sightings-list-container');
    if (!listEl) return;

    if (!sightings || sightings.length === 0) {
      listEl.innerHTML = `
        <div class="sighting-item">
          <div class="sighting-pin-location">
            <span class="pin-bullet">${pEmoji('pin', 'Location', 'sm')}</span>
            <div>
              <div class="sighting-location-text">No community sightings recorded yet</div>
              <div class="sighting-subtext">Be the first to record a sighting on campus!</div>
            </div>
          </div>
        </div>
      `;
      return;
    }

    listEl.innerHTML = sightings.map(s => `
      <div class="sighting-item">
        <div class="sighting-pin-location">
          <span class="pin-bullet">${pEmoji('pin', 'Location', 'sm')}</span>
          <div>
            <div class="sighting-location-text">${escapeHtml(canonicalCampusLocation(s.location_name || s.location))}</div>
            <div class="sighting-subtext">${escapeHtml(s.activity || 'Spotted')} ${s.note ? '• "' + escapeHtml(s.note) + '"' : ''}</div>
          </div>
        </div>
        <div class="sighting-time-badge">${escapeHtml(s.time_ago)}</div>
      </div>
    `).join('');
  }

  function populateLocationDropdowns(locations) {
    const select = document.getElementById('sighting-location-select');
    const reportSelect = document.getElementById('report-location-select');
    if (!select && !reportSelect) return;

    // Filter to canonical locations without duplicates
    const seenNames = new Set();
    const cleanList = [];
    (locations || []).forEach(loc => {
      const cleanName = canonicalCampusLocation(loc.name);
      if (!seenNames.has(cleanName)) {
        seenNames.add(cleanName);
        cleanList.push({ id: loc.id, name: cleanName });
      }
    });

    const optionsHtml = '<option value="">-- Choose campus location --</option>' +
      cleanList.map(loc => `<option value="${loc.id}">${escapeHtml(loc.name)}</option>`).join('');

    if (select) select.innerHTML = optionsHtml;
    if (reportSelect) reportSelect.innerHTML = optionsHtml;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Setup Event Handlers
  function setupEvents() {
    // Share / Copy Link
    const shareBtn = document.getElementById('btn-share-dog');
    if (shareBtn) {
      shareBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const shareData = {
          title: `${currentDogData?.name || 'Campus Dog'} (${currentDogUid}) — CU Campus Dogs`,
          text: `Digital Identity Profile for ${currentDogData?.name || 'Campus Dog'} at Chandigarh University`,
          url: window.location.href,
        };

        if (navigator.share) {
          try {
            await navigator.share(shareData);
            return;
          } catch (err) {
            // fallback to clipboard
          }
        }

        try {
          await navigator.clipboard.writeText(window.location.href);
          showToast(`Copied ${currentDogData?.name || 'dog'}'s profile link! ${pEmoji('paw', 'Paw', 'sm')}`);
        } catch (err) {
          showToast('Link ready: ' + window.location.href);
        }
      });
    }

    // Favorite Button
    const favBtn = document.getElementById('btn-favorite');
    if (favBtn) {
      const favKey = `dog_fav_${currentDogUid}`;
      let isFav = localStorage.getItem(favKey) === 'true';
      updateFavUI(isFav);

      favBtn.addEventListener('click', (e) => {
        e.preventDefault();
        isFav = !isFav;
        localStorage.setItem(favKey, isFav ? 'true' : 'false');
        updateFavUI(isFav);
        showToast(isFav ? `Added ${currentDogData?.name || 'dog'} to Favorites! ${pEmoji('heart_red', 'Heart', 'sm')}` : 'Removed from Favorites');
      });

      function updateFavUI(fav) {
        const heartSpan = favBtn.querySelector('.fav-heart');
        if (heartSpan) {
          heartSpan.innerHTML = fav ? pEmoji('heart_red', 'Favorite', 'sm') : pEmoji('heart_white', 'Not favorite', 'sm');
        }
      }
    }

    // Scroll to Location
    const viewLocBtn = document.getElementById('btn-view-location');
    if (viewLocBtn) {
      viewLocBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const mapCard = document.getElementById('last-spotted-section');
        if (mapCard) {
          mapCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
          mapCard.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
          mapCard.style.transform = 'scale(1.03) rotate(0deg)';
          setTimeout(() => {
            mapCard.style.transform = '';
          }, 1000);
        }
      });
    }

    // Open Sighting Modal (CTA button, Add Entry button, or any /sighting links)
    const openSightingModal = (e) => {
      if (e) e.preventDefault();
      if (sightingModal) sightingModal.classList.add('active');
    };

    const sawDogBtn = document.getElementById('btn-saw-dog');
    if (sawDogBtn) sawDogBtn.addEventListener('click', openSightingModal);

    const addSightingBtn = document.getElementById('btn-add-sighting');
    if (addSightingBtn) addSightingBtn.addEventListener('click', openSightingModal);

    document.querySelectorAll('a[href$="/sighting"]').forEach(link => {
      link.addEventListener('click', openSightingModal);
    });

    // Open Report Modal
    const openReportModal = (e) => {
      if (e) e.preventDefault();
      if (reportModal) reportModal.classList.add('active');
    };

    const reportBtn = document.getElementById('btn-report-issue');
    if (reportBtn) reportBtn.addEventListener('click', openReportModal);

    document.querySelectorAll('a[href$="/report"]').forEach(link => {
      link.addEventListener('click', openReportModal);
    });

    // Admin Quick Edit Dog Modal
    const editDogModal = document.getElementById('edit-dog-modal');
    const openEditDogModal = (e) => {
      if (e) e.preventDefault();
      if (editDogModal) editDogModal.classList.add('active');
    };

    ['open-edit-dog-btn', 'open-edit-dog-btn-bar', 'open-edit-dog-btn-hero'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) btn.addEventListener('click', openEditDogModal);
    });

    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    if (cancelEditBtn && editDogModal) {
      cancelEditBtn.addEventListener('click', () => {
        editDogModal.classList.remove('active');
      });
    }

    const closeEditBtn = document.getElementById('close-edit-modal-btn');
    if (closeEditBtn && editDogModal) {
      closeEditBtn.addEventListener('click', () => {
        editDogModal.classList.remove('active');
      });
    }

    // Check URL params for direct modal launch or flash messages
    const urlParams = new URLSearchParams(window.location.search);
    const flashMsg = urlParams.get('msg');
    if (flashMsg) {
      showToast(decodeURIComponent(flashMsg));
    }

    if (urlParams.get('modal') === 'sighting' || window.location.hash === '#sighting') {
      openSightingModal();
    } else if (urlParams.get('modal') === 'report' || window.location.hash === '#report') {
      openReportModal();
    } else if (urlParams.get('modal') === 'edit') {
      openEditDogModal();
    }

    // Close Modals
    document.querySelectorAll('.modal-close-btn, .modal-cancel-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (sightingModal) sightingModal.classList.remove('active');
        if (reportModal) reportModal.classList.remove('active');
        if (editDogModal) editDogModal.classList.remove('active');
      });
    });

    // Close when clicking outside card
    window.addEventListener('click', (e) => {
      if (e.target === sightingModal) sightingModal.classList.remove('active');
      if (e.target === reportModal) reportModal.classList.remove('active');
      if (e.target === editDogModal) editDogModal.classList.remove('active');
    });

    // Activity Chips Selection
    document.querySelectorAll('.activity-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.activity-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        activeActivity = chip.getAttribute('data-activity') || 'Resting';
      });
    });

    // Sighting Form Submit
    const sightingForm = document.getElementById('sighting-form');
    if (sightingForm) {
      sightingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const locSelect = document.getElementById('sighting-location-select');
        const customLocInput = document.getElementById('sighting-custom-location');
        const noteInput = document.getElementById('sighting-note');
        const submitterInput = document.getElementById('sighting-submitter');

        const locId = locSelect?.value ? parseInt(locSelect.value, 10) : null;
        const locName = (!locId && customLocInput?.value.trim()) ? customLocInput.value.trim() : null;

        if (!locId && !locName) {
          alert('Please pick a campus location or enter one below!');
          return;
        }

        const payload = {
          location_id: locId,
          location_name: locName,
          activity: activeActivity,
          note: noteInput?.value.trim() || null,
          submitted_by: submitterInput?.value.trim() || 'Campus Student',
        };

        const submitBtn = document.getElementById('sighting-submit-btn');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = `Saving Sighting... ${pEmoji('paw', 'Paw', 'sm')}`;
        }

        try {
          const res = await fetch(`/api/dogs/${encodeURIComponent(currentDogUid)}/sightings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });

          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Failed to submit sighting');
          }

          showToast(`Sighting saved! Thank you for watching out for ${currentDogData?.name || 'Bruno'}! ${pEmoji('paw', 'Paw', 'sm')}`);
          if (sightingModal) sightingModal.classList.remove('active');
          sightingForm.reset();

          // Refresh profile & sightings immediately
          await loadDogProfile();
          await loadSightings();
        } catch (err) {
          alert(`Could not save sighting: ${err.message}`);
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save Sighting ➔';
          }
        }
      });
    }

    // Report Form Submit
    const reportForm = document.getElementById('report-form');
    if (reportForm) {
      reportForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const typeSelect = document.getElementById('report-type-select');
        const severitySelect = document.getElementById('report-severity-select');
        const locSelect = document.getElementById('report-location-select');
        const descInput = document.getElementById('report-description');
        const submitterInput = document.getElementById('report-submitter');
        const contactInput = document.getElementById('report-contact');

        if (!descInput || !descInput.value.trim()) {
          alert('Please describe the situation or injury so staff can assist.');
          return;
        }

        const payload = {
          report_type: typeSelect?.value || 'INJURED',
          severity: severitySelect?.value || 'MEDIUM',
          description: descInput.value.trim(),
          location_id: locSelect?.value ? parseInt(locSelect.value, 10) : null,
          submitted_by: submitterInput?.value.trim() || 'Campus Member',
          contact_info: contactInput?.value.trim() || null,
        };

        const submitBtn = document.getElementById('report-submit-btn');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = `Sending to RoboX Care... ${pEmoji('siren', 'Alert', 'sm')}`;
        }

        try {
          const res = await fetch(`/api/dogs/${encodeURIComponent(currentDogUid)}/reports`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });

          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Failed to submit report');
          }

          showToast(`Urgent report sent to CU RoboX Care Team. Thank you! ${pEmoji('paw', 'Paw', 'sm')}`);
          if (reportModal) reportModal.classList.remove('active');
          reportForm.reset();
        } catch (err) {
          alert(`Could not submit report: ${err.message}`);
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Send Report ➔';
          }
        }
      });
    }
  }

  // Time-aware Campus Map (Day: 8 AM - 8 PM, Night: 8 PM - 8 AM)
  function initTimeBasedMap() {
    const mapImg = document.getElementById('campus-map-img');
    const timeIcon = document.getElementById('map-time-icon');
    const timeLabel = document.getElementById('map-time-label');
    const toggleBtn = document.getElementById('map-toggle-btn');
    const modalMapImg = document.getElementById('sighting-modal-map-img');
    const modalMapLabel = document.getElementById('sighting-modal-map-label');
    const modalMapIcon = document.getElementById('sighting-modal-map-icon');

    if (!mapImg) return;

    const DAY_SRC = '/static/assets/maps/campus-map-day.png';
    const NIGHT_SRC = '/static/assets/maps/campus-map-night.png';

    function setMapMode(mode, animate = false) {
      const isDay = (mode === 'day');
      const targetSrc = isDay ? DAY_SRC : NIGHT_SRC;
      const targetLabel = isDay ? 'Day View (8 AM–8 PM)' : 'Night View (8 PM–8 AM)';
      const targetIcon = isDay ? pEmoji('sun', 'Daytime', 'sm') : pEmoji('moon', 'Nighttime', 'sm');

      if (animate) {
        mapImg.style.opacity = '0.35';
        setTimeout(() => {
          mapImg.src = targetSrc;
          mapImg.setAttribute('data-mode', mode);
          mapImg.style.opacity = '1';
        }, 180);
      } else {
        mapImg.src = targetSrc;
        mapImg.setAttribute('data-mode', mode);
      }

      if (timeIcon) timeIcon.innerHTML = targetIcon;
      if (timeLabel) timeLabel.textContent = targetLabel;
      if (modalMapImg) modalMapImg.src = targetSrc;
      if (modalMapLabel) modalMapLabel.textContent = targetLabel;
      if (modalMapIcon) modalMapIcon.innerHTML = targetIcon;
    }

    // Determine current mode by local client time
    const now = new Date();
    const hour = now.getHours();
    const autoMode = (hour >= 8 && hour < 20) ? 'day' : 'night';
    setMapMode(autoMode, false);

    // Toggle button handler
    if (toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const currentMode = mapImg.getAttribute('data-mode') || autoMode;
        const newMode = (currentMode === 'day') ? 'night' : 'day';
        setMapMode(newMode, true);
        showToast(`Switched to ${newMode === 'day' ? pEmoji('sun', 'Sun', 'sm') + ' Daytime' : pEmoji('moon', 'Moon', 'sm') + ' Nighttime'} Campus Map view!`);
      });
    }
  }

  // Clean Zoomable Campus Map Engine (Fitted default, zoom/pan bounded within map)
  function initMapZoomAndPan() {
    const viewport = document.getElementById('campus-map-viewport');
    const canvas = document.getElementById('campus-map-canvas');
    if (!viewport || !canvas) return;

    let scale = 1.0;
    const minScale = 1.0;
    const maxScale = 4.0;
    let panX = 0;
    let panY = 0;
    let isMouseDown = false;

    function clamp(val, min, max) {
      return Math.max(min, Math.min(max, val));
    }

    function updateTransform(smooth = false) {
      const vRect = viewport.getBoundingClientRect();
      if (scale <= 1.01) {
        scale = 1.0;
        panX = 0;
        panY = 0;
      } else {
        const minPanX = vRect.width * (1 - scale);
        const minPanY = vRect.height * (1 - scale);
        // Strictly lock within fitted map area: no blank borders or gaps ever exposed
        panX = Math.min(0, Math.max(minPanX, panX));
        panY = Math.min(0, Math.max(minPanY, panY));
      }

      if (smooth) {
        canvas.classList.add('smooth-transition');
        setTimeout(() => canvas.classList.remove('smooth-transition'), 300);
      } else {
        canvas.classList.remove('smooth-transition');
      }

      canvas.style.transform = `translate3d(${panX.toFixed(2)}px, ${panY.toFixed(2)}px, 0px) scale(${scale.toFixed(3)})`;
      viewport.style.cursor = scale > 1.01 ? (isMouseDown ? 'grabbing' : 'grab') : 'default';
    }

    function zoomAtPoint(newScale, clientX, clientY, smooth = false) {
      newScale = clamp(newScale, minScale, maxScale);

      // If user zooms out all the way, snap cleanly to fully fitted
      if (newScale <= 1.02) {
        scale = 1.0;
        panX = 0;
        panY = 0;
        updateTransform(smooth);
        return;
      }

      if (Math.abs(newScale - scale) < 0.0005) return;

      const vRect = viewport.getBoundingClientRect();
      const cx = (clientX !== undefined ? clientX : (vRect.left + vRect.width / 2)) - vRect.left;
      const cy = (clientY !== undefined ? clientY : (vRect.top + vRect.height / 2)) - vRect.top;

      panX = cx - ((cx - panX) / scale) * newScale;
      panY = cy - ((cy - panY) / scale) * newScale;
      scale = newScale;

      updateTransform(smooth);
    }

    // Mouse Wheel Zoom (Desktop & Trackpad)
    viewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      let zoomFactor;
      if (e.ctrlKey) {
        zoomFactor = Math.exp(-e.deltaY * 0.015);
      } else {
        zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      }
      zoomAtPoint(scale * zoomFactor, e.clientX, e.clientY, false);
    }, { passive: false });

    // Double-click toggle zoom (Desktop)
    viewport.addEventListener('dblclick', (e) => {
      e.preventDefault();
      if (scale > 1.05) {
        scale = 1.0;
        panX = 0;
        panY = 0;
        updateTransform(true);
      } else {
        zoomAtPoint(2.2, e.clientX, e.clientY, true);
      }
    });

    // Desktop Mouse Drag Panning (Active only when zoomed in)
    let startMouseX = 0;
    let startMouseY = 0;
    let startPanX = 0;
    let startPanY = 0;

    viewport.addEventListener('mousedown', (e) => {
      if (e.button !== 0 || scale <= 1.001) return;
      isMouseDown = true;
      startMouseX = e.clientX;
      startMouseY = e.clientY;
      startPanX = panX;
      startPanY = panY;
      viewport.classList.add('is-dragging');
      viewport.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', (e) => {
      if (!isMouseDown) return;
      panX = startPanX + (e.clientX - startMouseX);
      panY = startPanY + (e.clientY - startMouseY);
      updateTransform(false);
    });

    window.addEventListener('mouseup', () => {
      if (isMouseDown) {
        isMouseDown = false;
        viewport.classList.remove('is-dragging');
        viewport.style.cursor = scale > 1.001 ? 'grab' : 'default';
      }
    });

    // Touch Pinch-to-Zoom & Pan (Mobile 2 Fingers & Drag)
    let initialPinchDist = 0;
    let initialPinchScale = 1.0;
    let pinchCenterX = 0;
    let pinchCenterY = 0;
    let lastTouchX = 0;
    let lastTouchY = 0;
    let lastTapTime = 0;

    viewport.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        const now = Date.now();
        const t = e.touches[0];
        // Double-tap zoom toggle
        if (now - lastTapTime < 300) {
          e.preventDefault();
          if (scale > 1.05) {
            scale = 1.0;
            panX = 0;
            panY = 0;
            updateTransform(true);
          } else {
            zoomAtPoint(2.2, t.clientX, t.clientY, true);
          }
          lastTapTime = 0;
          return;
        }
        lastTapTime = now;

        lastTouchX = t.clientX;
        lastTouchY = t.clientY;
        startPanX = panX;
        startPanY = panY;
      } else if (e.touches.length === 2) {
        e.preventDefault();
        const t1 = e.touches[0];
        const t2 = e.touches[1];
        initialPinchDist = Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
        initialPinchScale = scale;
        pinchCenterX = (t1.clientX + t2.clientX) / 2;
        pinchCenterY = (t1.clientY + t2.clientY) / 2;
        startPanX = panX;
        startPanY = panY;
      }
    }, { passive: false });

    viewport.addEventListener('touchmove', (e) => {
      if (e.touches.length === 1 && scale > 1.001) {
        e.preventDefault(); // Pan map when zoomed without jumping page
        const t = e.touches[0];
        panX += (t.clientX - lastTouchX);
        panY += (t.clientY - lastTouchY);
        lastTouchX = t.clientX;
        lastTouchY = t.clientY;
        updateTransform(false);
      } else if (e.touches.length === 2) {
        e.preventDefault(); // Two-finger pinch to zoom in/out
        const t1 = e.touches[0];
        const t2 = e.touches[1];
        const currentDist = Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
        if (initialPinchDist > 0) {
          const factor = currentDist / initialPinchDist;
          const targetScale = clamp(initialPinchScale * factor, minScale, maxScale);
          zoomAtPoint(targetScale, pinchCenterX, pinchCenterY, false);
        }
      }
    }, { passive: false });

    viewport.addEventListener('touchend', (e) => {
      if (e.touches.length === 0) {
        updateTransform(true);
      }
    });

    // Floating Zoom and Fit Buttons (+, -, Fit)
    const zoomInBtn = document.getElementById('map-zoom-in-btn');
    const zoomOutBtn = document.getElementById('map-zoom-out-btn');
    const zoomFitBtn = document.getElementById('map-zoom-fit-btn');

    if (zoomInBtn) {
      zoomInBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const vRect = viewport.getBoundingClientRect();
        zoomAtPoint(scale * 1.35, vRect.left + vRect.width / 2, vRect.top + vRect.height / 2, true);
      });
    }

    if (zoomOutBtn) {
      zoomOutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const nextScale = scale / 1.35;
        if (nextScale <= 1.05) {
          scale = 1.0;
          panX = 0;
          panY = 0;
          updateTransform(true);
        } else {
          const vRect = viewport.getBoundingClientRect();
          zoomAtPoint(nextScale, vRect.left + vRect.width / 2, vRect.top + vRect.height / 2, true);
        }
      });
    }

    if (zoomFitBtn) {
      zoomFitBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        scale = 1.0;
        panX = 0;
        panY = 0;
        updateTransform(true);
      });
    }

    window.addEventListener('resize', () => {
      updateTransform(false);
    });

    // Initialize map in perfectly fitted state
    updateTransform(false);
  }

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    setupEvents();
    initTimeBasedMap();
    initMapZoomAndPan();
    loadDogProfile();
    loadSightings();
    loadCampusLocations();
  });
})();
