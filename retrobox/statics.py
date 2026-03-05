"""RetroBox shared static assets (CSS + JS).

These strings are embedded verbatim into every generated controller HTML page.
They provide:
  • Full layout / zone / button / dpad / joystick styles (CSS)
  • Touch, mouse, keyboard input handling + joystick + dpad animations (JS)

Import and use in any generator or custom pipeline:

    from retrobox.statics import STATIC_CSS, STATIC_JS

The JS block expects two variables already declared above it in the same
<script> tag:

    SVG_W   — viewport width  (integer)
    SVG_H   — viewport height (integer)
    ZONES   — array of zone descriptor objects (from TouchZone.to_dict())
    KEY_MAP — object mapping KeyboardEvent.key → zone id string
"""

# ---------------------------------------------------------------------------
# CSS — no dynamic values; background is set via --rb-bg custom property
# ---------------------------------------------------------------------------
STATIC_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100%; height: 100%; overflow: hidden;
      background: var(--rb-bg, #000);
      touch-action: none;
      -webkit-touch-callout: none;
      -webkit-user-select: none;
      user-select: none;
    }

    .rb-container {
      position: relative;
      width: 100vw; height: 100vh;
      display: flex; justify-content: center; align-items: center;
    }
    .rb-container .rb-svg {
      width: 100%; height: 100%;
      object-fit: contain;
      object-position: center top;
      pointer-events: none;
    }

    /* ── Touch layer + generic zone ──────────────────────── */
    .rb-touch-layer { position: absolute; }
    .rb-zone {
      position: absolute;
      background: transparent;
      border: none; outline: none;
      -webkit-tap-highlight-color: transparent;
      z-index: 10;
      pointer-events: auto;
      transition: transform 0.07s ease, box-shadow 0.07s ease, background 0.07s ease;
      will-change: transform;
    }
    .rb-zone.active {
      background: rgba(255,255,255,0.15);
      transform: scale(0.82);
    }
    .rb-zone[data-shape="round"]  { border-radius: 50%; }
    .rb-zone[data-shape="round"].active {
      box-shadow: 0 0 18px 6px rgba(255,255,255,0.4);
    }
    .rb-zone[data-shape="pill"]   { border-radius: 999px; }
    .rb-zone[data-shape="pill"].active {
      box-shadow: 0 0 12px 4px rgba(255,255,255,0.25);
    }

    /* ── D-pad ───────────────────────────────────────────── */
    .rb-zone[data-type="dpad"] {
      transition: transform 0.05s ease, background 0.05s ease, box-shadow 0.05s ease;
    }
    .rb-zone[data-type="dpad"].active {
      transform: scale(0.76);
      background: rgba(255,255,255,0.22) !important;
      box-shadow: inset 0 0 8px rgba(255,255,255,0.18);
    }

    /* ── Joystick zone ───────────────────────────────────── */
    /* The zone itself is invisible; visuals live in child divs */
    .rb-zone[data-type="joystick"] {
      background: transparent !important;
      box-shadow: none !important;
      transform: none !important;
      overflow: visible;
    }
    /* Base ring — animates in on touch, fully transparent by default */
    .rb-joystick-base {
      position: absolute;
      border-radius: 50%;
      border: 2px solid transparent;
      background: transparent;
      pointer-events: none;
      opacity: 0;
      transform: scale(0.7);
      transition: opacity 0.14s ease, transform 0.14s cubic-bezier(0.2,0,0.2,1.5);
      will-change: opacity, transform;
    }
    .rb-joystick-base.visible {
      opacity: 1;
      transform: scale(1);
    }
    /* Moveable puck — fixed to zone centre, eases back on release */
    .rb-joystick-knob {
      position: absolute;
      width: 44%; height: 44%;
      background: #000;
      border-radius: 50%;
      top: 50%; left: 50%;
      transform: translate(-50%,-50%);
      pointer-events: none;
      transition: transform 0.10s cubic-bezier(0.2,0,0.2,1.5);
      will-change: transform;
      box-shadow: 0 2px 8px rgba(0,0,0,0.6);
    }
    /* Remove easing while finger is actively dragging */
    .rb-joystick-knob.dragging { transition: none; }

    /* ── Menu trigger ────────────────────────────────────── */
    .rb-zone[data-type="menu_trigger"] {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .rb-zone[data-type="menu_trigger"] .active {
      background: transparent;
      transform: none;
      box-shadow: none;
    }
    /* Logo image inside the tab button */
    .rb-tab-logo {
      height: 79%;
      width: auto;
      max-width: 90%;
      pointer-events: none;
      user-select: none;
      -webkit-user-select: none;
      display: block;
    }

    /* ── Overlay menu ────────────────────────────────────── */
    .rb-menu-overlay {
      position: fixed; top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(0,0,0,0.55);
      z-index: 100;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.22s ease;
    }
    .rb-menu-overlay.open {
      opacity: 1;
      pointer-events: auto;
    }
    /* Card slides down from the top */
    .rb-menu-card {
      position: absolute;
      top: 0;
      background: #d8d8d8;
      border-radius: 0 0 16px 16px;
      padding: 14px;
      min-width: 200px;
      border: 1px solid #aaa;
      border-top: none;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      display: flex;
      flex-direction: column;
      gap: 10px;
      transform: translateY(-110%);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .rb-menu-overlay.open .rb-menu-card {
      transform: translateY(0);
    }
    .rb-menu-item {
      display: block; width: 100%;
      padding: 12px 24px;
      border: none;
      background: #f4f4f4;
      border-radius: 30px;
      font-size: 16px; text-align: center; cursor: pointer;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      box-shadow: 0 2px 4px rgba(0,0,0,0.08);
      transition: transform 0.1s, background 0.1s;
    }
    .rb-menu-item:active { background: #e0e0e0; transform: scale(0.98); }
    .rb-menu-item.danger  { color: #d32f2f; }
    .rb-menu-item.default { color: #222; }
    .rb-menu-divider { height: 1px; background: #bbb; margin: 0 8px; }
    .rb-menu-logo {
      display: flex; align-items: center; justify-content: center;
      gap: 10px; padding: 4px 8px 0px;
    }
    .rb-menu-logo img  { height: 32px; }
"""

# ---------------------------------------------------------------------------
# JS — expects SVG_W, SVG_H, ZONES, KEY_MAP declared before this block
# ---------------------------------------------------------------------------
STATIC_JS = r"""
    /* ── state ───────────────────────────────────────────── */
    const activeTouches = new Map();   // touchId → zone el (buttons / joystick)
    let mouseZone = null;
    let menuOpen  = false;

    const touchLayer   = document.getElementById('rb-touch-layer');
    const menuOverlay  = document.getElementById('rb-menu-overlay');
    const menuCard     = document.getElementById('rb-menu-card');

    /* ── positioning ─────────────────────────────────────── */
    function positionZones() {
      const ct = document.getElementById('rb-container');
      const cW = ct.clientWidth, cH = ct.clientHeight;
      const scale = Math.min(cW / SVG_W, cH / SVG_H);
      const rW = SVG_W * scale, rH = SVG_H * scale;
      const oX = (cW - rW) / 2, oY = 0;

      touchLayer.style.left   = oX + 'px';
      touchLayer.style.top    = oY + 'px';
      touchLayer.style.width  = rW + 'px';
      touchLayer.style.height = rH + 'px';

      for (var i = 0; i < ZONES.length; i++) {
        var z  = ZONES[i];
        var el = document.getElementById('zone-' + z.id);
        if (!el) continue;
        el.style.left   = (z.x / SVG_W * 100) + '%';
        el.style.top    = (z.y / SVG_H * 100) + '%';
        el.style.width  = (z.w / SVG_W * 100) + '%';
        el.style.height = (z.h / SVG_H * 100) + '%';
      }
    }

    /* ── hit testing ─────────────────────────────────────── */
    function hitZone(cx, cy) {
      var els = touchLayer.querySelectorAll('.rb-zone');
      for (var i = 0; i < els.length; i++) {
        var r = els[i].getBoundingClientRect();
        if (cx >= r.left && cx <= r.right && cy >= r.top && cy <= r.bottom) {
          return els[i];
        }
      }
      return null;
    }

    /* ── activate / deactivate ───────────────────────────── */
    function activate(el) {
      if (el.dataset.type === 'menu_trigger') { openMenu(); return; }
      el.classList.add('active');
    }
    function deactivate(el) {
      el.classList.remove('active');
    }

    /* ── menu ────────────────────────────────────────────── */
    function positionMenuCard() {
      var trigger = document.getElementById('zone-menu-trigger');
      if (!trigger || !menuCard) return;
      var tr = trigger.getBoundingClientRect();
      menuCard.style.left  = tr.left + 'px';
      menuCard.style.width = tr.width + 'px';
    }

    /* ── D-pad: axis-dominance + diagonal + neutral zone ─── */
    var dpadCenter  = null;   // screen {x,y} of dpad group centre
    var dpadRadius  = 0;      // half-width of full dpad bounding box (px)
    var dpadTouchId = null;   // touch owning the dpad (null = idle)
    var DPAD_DEAD   = 0.15;   // neutral-zone fraction of dpadRadius
    var DPAD_DIAG   = 0.42;   // diagonal threshold (normalised axis component)

    function prepareDpad() {
      var zones = touchLayer.querySelectorAll('.rb-zone[data-type="dpad"]');
      if (!zones.length) return;
      var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (var i = 0; i < zones.length; i++) {
        var r = zones[i].getBoundingClientRect();
        minX = Math.min(minX, r.left);  minY = Math.min(minY, r.top);
        maxX = Math.max(maxX, r.right); maxY = Math.max(maxY, r.bottom);
      }
      dpadCenter = { x: (minX + maxX) / 2, y: (minY + maxY) / 2 };
      dpadRadius = (maxX - minX) / 2;
    }

    function dpadDirsAt(cx, cy) {
      if (!dpadCenter) return [];
      var dx = cx - dpadCenter.x, dy = cy - dpadCenter.y;
      var dist = Math.hypot(dx, dy);
      if (dist < dpadRadius * DPAD_DEAD) return [];
      var nx = dx / dist, ny = dy / dist;
      var ax = Math.abs(nx), ay = Math.abs(ny);
      if (ax > DPAD_DIAG && ay > DPAD_DIAG)
        return [(nx > 0 ? 'right' : 'left'), (ny > 0 ? 'down' : 'up')];
      if (ax >= ay) return [nx > 0 ? 'right' : 'left'];
      return [ny > 0 ? 'down' : 'up'];
    }

    function applyDpadDirs(dirs) {
      var set = {};
      for (var i = 0; i < dirs.length; i++) set[dirs[i]] = true;
      var zones = touchLayer.querySelectorAll('.rb-zone[data-type="dpad"]');
      for (var i = 0; i < zones.length; i++) {
        var z  = zones[i];
        var zd = (z.dataset.directions || '').split(',').filter(Boolean);
        var match = (zd.length === dirs.length) && zd.every(function(d) { return set[d]; });
        if (match) z.classList.add('active');
        else       z.classList.remove('active');
      }
    }

    /* ── Analog joystick (fixed-centre, puck follows finger) ─ */
    var jsZone    = null;   // joystick zone element
    var jsKnob    = null;   // moving puck div
    var jsBase    = null;   // base ring div
    var jsTouchId = null;   // touch identifier (null = idle, -1 = mouse)
    var jsAnchorX = 0;      // anchor x in zone-local px (= zone centre)
    var jsAnchorY = 0;      // anchor y in zone-local px (= zone centre)
    var jsMaxR    = 0;      // max travel radius (px)
    var jsTimer   = null;   // snap-back cleanup timer

    function prepareAnalog() {
      jsZone = document.querySelector('.rb-zone[data-type="joystick"]');
      if (!jsZone) return;
      jsKnob = jsZone.querySelector('.rb-joystick-knob');
      jsBase = jsZone.querySelector('.rb-joystick-base');
      _jsReset();
    }

    function _jsReset() {
      if (jsKnob) { jsKnob.classList.remove('dragging'); jsKnob.style.transform = ''; }
      if (jsBase) { jsBase.classList.remove('visible');  jsBase.style.cssText = ''; }
      jsAnchorX = 0; jsAnchorY = 0; jsMaxR = 0;
    }

    function jsActivate(cx, cy) {
      if (!jsZone) return;
      if (jsTimer) { clearTimeout(jsTimer); jsTimer = null; }
      var r = jsZone.getBoundingClientRect();
      jsMaxR    = r.width * 0.34;
      jsAnchorX = r.width  / 2;   // always fixed to zone centre
      jsAnchorY = r.height / 2;
      if (jsBase) {
        var sz = jsMaxR * 2;
        jsBase.style.left   = (jsAnchorX - jsMaxR) + 'px';
        jsBase.style.top    = (jsAnchorY - jsMaxR) + 'px';
        jsBase.style.width  = sz + 'px';
        jsBase.style.height = sz + 'px';
        jsBase.classList.add('visible');
      }
      if (jsKnob) { jsKnob.classList.add('dragging'); _jsKnobTo(0, 0); }
    }

    function _jsKnobTo(dx, dy) {
      if (!jsKnob || !jsZone) return;
      var r  = jsZone.getBoundingClientRect();
      var ox = jsAnchorX + dx - r.width  * 0.5;
      var oy = jsAnchorY + dy - r.height * 0.5;
      jsKnob.style.transform =
        'translate(calc(-50% + ' + ox + 'px), calc(-50% + ' + oy + 'px))';
    }

    function moveKnob(cx, cy) {
      if (!jsZone || !jsKnob || jsTouchId === null) return;
      var r  = jsZone.getBoundingClientRect();
      var dx = cx - r.left - jsAnchorX;
      var dy = cy - r.top  - jsAnchorY;
      var d  = Math.hypot(dx, dy);
      if (d > jsMaxR) { dx = dx / d * jsMaxR; dy = dy / d * jsMaxR; }
      _jsKnobTo(dx, dy);
    }

    function resetKnob() {
      if (!jsKnob) return;
      jsTouchId = null;
      jsKnob.classList.remove('dragging');  // re-enable CSS ease
      _jsKnobTo(0, 0);                      // animate puck back to anchor
      if (jsTimer) clearTimeout(jsTimer);
      jsTimer = setTimeout(function() {     // then fully reset when done
        jsTimer = null;
        _jsReset();
      }, 140);
    }

    /* ── init + resize ───────────────────────────────────── */
    window.addEventListener('load',   function() { positionZones(); prepareDpad(); prepareAnalog(); });
    window.addEventListener('resize', function() { positionZones(); prepareDpad(); prepareAnalog(); });

    /* ── menu helpers ────────────────────────────────────── */
    function openMenu() {
      if (!menuOverlay) return;
      positionMenuCard();
      menuOpen = true;
      menuOverlay.classList.add('open');
    }
    function closeMenu() {
      if (!menuOverlay) return;
      menuOpen = false;
      menuOverlay.classList.remove('open');
      activeTouches.forEach(function(el) { deactivate(el); });
      activeTouches.clear();
      if (mouseZone) { deactivate(mouseZone); mouseZone = null; }
      applyDpadDirs([]); dpadTouchId = null;
      if (jsTouchId !== null) resetKnob();
    }

    if (menuOverlay) {
      menuOverlay.addEventListener('touchstart', function(e) {
        if (e.target === menuOverlay) { e.preventDefault(); closeMenu(); }
      }, { passive: false });
      menuOverlay.addEventListener('click', function(e) {
        if (e.target === menuOverlay) closeMenu();
      });
      if (menuCard) {
        menuCard.addEventListener('click', function(e) {
          if (e.target.classList.contains('rb-menu-item')) closeMenu();
        });
        menuCard.addEventListener('touchend', function(e) {
          if (e.target.classList.contains('rb-menu-item')) {
            e.preventDefault(); closeMenu();
          }
        }, { passive: false });
      }
    }

    /* Release all inputs when the app is backgrounded */
    document.addEventListener('visibilitychange', function() {
      if (document.hidden) {
        applyDpadDirs([]); dpadTouchId = null;
        if (jsTouchId !== null) resetKnob();
        activeTouches.forEach(function(el) { deactivate(el); });
        activeTouches.clear();
        if (mouseZone) { deactivate(mouseZone); mouseZone = null; }
      }
    });

    /* ── touch events ────────────────────────────────────── */
    document.addEventListener('touchstart', function(e) {
      if (menuOpen) return;
      e.preventDefault();
      for (var i = 0; i < e.changedTouches.length; i++) {
        var t = e.changedTouches[i];
        var z = hitZone(t.clientX, t.clientY);
        if (!z) continue;
        if (z.dataset.type === 'dpad' && dpadTouchId === null) {
          dpadTouchId = t.identifier;
          applyDpadDirs(dpadDirsAt(t.clientX, t.clientY));
        } else if (z.dataset.type === 'joystick' && jsTouchId === null) {
          jsTouchId = t.identifier;
          activate(z);
          jsActivate(t.clientX, t.clientY);
          activeTouches.set(t.identifier, z);
        } else if (z.dataset.type !== 'dpad' && z.dataset.type !== 'joystick') {
          activeTouches.set(t.identifier, z);
          activate(z);
        }
      }
    }, { passive: false });

    document.addEventListener('touchmove', function(e) {
      if (menuOpen) return;
      e.preventDefault();
      for (var i = 0; i < e.changedTouches.length; i++) {
        var t = e.changedTouches[i];
        if (t.identifier === dpadTouchId) {
          applyDpadDirs(dpadDirsAt(t.clientX, t.clientY));
        } else if (t.identifier === jsTouchId) {
          moveKnob(t.clientX, t.clientY);
        }
      }
    }, { passive: false });

    function _touchRelease(id) {
      if (id === dpadTouchId) {
        applyDpadDirs([]); dpadTouchId = null;
      } else if (id === jsTouchId) {
        resetKnob();
        var z = activeTouches.get(id);
        if (z) { deactivate(z); activeTouches.delete(id); }
      } else {
        var z = activeTouches.get(id);
        if (z) { deactivate(z); activeTouches.delete(id); }
      }
    }
    document.addEventListener('touchend', function(e) {
      for (var i = 0; i < e.changedTouches.length; i++)
        _touchRelease(e.changedTouches[i].identifier);
    }, { passive: false });
    document.addEventListener('touchcancel', function(e) {
      for (var i = 0; i < e.changedTouches.length; i++)
        _touchRelease(e.changedTouches[i].identifier);
    });

    /* ── mouse events (desktop testing) ──────────────────── */
    document.addEventListener('mousedown', function(e) {
      if (menuOpen) return;
      var z = hitZone(e.clientX, e.clientY);
      if (!z) return;
      mouseZone = z;
      if (z.dataset.type === 'dpad') {
        applyDpadDirs(dpadDirsAt(e.clientX, e.clientY));
      } else if (z.dataset.type === 'joystick') {
        activate(z);
        jsTouchId = -1;
        jsActivate(e.clientX, e.clientY);
      } else {
        activate(z);
      }
    });
    document.addEventListener('mousemove', function(e) {
      if (!mouseZone || menuOpen) return;
      if (mouseZone.dataset.type === 'dpad') {
        applyDpadDirs(dpadDirsAt(e.clientX, e.clientY)); return;
      }
      if (mouseZone.dataset.type === 'joystick') {
        moveKnob(e.clientX, e.clientY); return;
      }
      var curr = hitZone(e.clientX, e.clientY);
      if (mouseZone !== curr) {
        deactivate(mouseZone); mouseZone = null;
        if (curr) { mouseZone = curr; activate(curr); }
      }
    });
    document.addEventListener('mouseup', function() {
      if (!mouseZone) return;
      if (mouseZone.dataset.type === 'dpad') {
        applyDpadDirs([]);
      } else if (mouseZone.dataset.type === 'joystick') {
        resetKnob(); deactivate(mouseZone);
      } else {
        deactivate(mouseZone);
      }
      mouseZone = null;
    });

    /* ── keyboard events ─────────────────────────────────── */
    document.addEventListener('keydown', function(e) {
      if (menuOpen) return;
      var zid = KEY_MAP[e.key];
      if (zid) {
        e.preventDefault();
        var el = document.getElementById('zone-' + zid);
        if (el && !el.classList.contains('active')) activate(el);
      }
    });
    document.addEventListener('keyup', function(e) {
      var zid = KEY_MAP[e.key];
      if (zid) {
        e.preventDefault();
        var el = document.getElementById('zone-' + zid);
        if (el) deactivate(el);
      }
    });
"""
