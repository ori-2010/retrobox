"""HTML generator for RetroBox controller UIs.

Produces a single self-contained index.html that:
  • Renders the controller SVG with object-fit: contain.
  • Overlays invisible touch zones positioned via JavaScript.
  • Tracks multi-touch properly (no drag-lock).
  • Optional overlay menu triggered from a logo zone.
  • Keyboard support for desktop testing.
"""

import json
import os
from urllib.parse import quote

# location of the project root; used for resolving shared assets
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from .models import ControllerConfig, ZoneType
# CSS and JS live in retrobox/statics.py — imported as the canonical source.
# Any new controller generator should import from there directly.
from .statics import STATIC_CSS as _STATIC_CSS, STATIC_JS as _STATIC_JS

# ---------------------------------------------------------------------------
# Inline copies below are kept only as readable reference and are NOT used
# (they are assigned to _REMOVED_* so they don't shadow the imports above).
# To change the animations/styles, edit retrobox/statics.py.
# ---------------------------------------------------------------------------
_REMOVED_CSS = """
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

    /* Touch layer */
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
    /* D-pad cells — snappy press feedback */
    .rb-zone[data-type="dpad"] {
      transition: transform 0.05s ease, background 0.05s ease, box-shadow 0.05s ease;
    }
    .rb-zone[data-type="dpad"].active {
      transform: scale(0.76);
      background: rgba(255,255,255,0.22) !important;
      box-shadow: inset 0 0 8px rgba(255,255,255,0.18);
    }
    /* Joystick zone — transparent; visuals are the base+knob children */
    .rb-zone[data-type="joystick"] {
      background: transparent !important;
      box-shadow: none !important;
      transform: none !important;
      overflow: visible;
    }
    /* Floating base ring — appears where user first touches */
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
    /* Moveable puck */
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
    /* Suppress easing while finger is dragging */
    .rb-joystick-knob.dragging { transition: none; }
    /* Menu trigger — no press effect, it just opens the menu */
    .rb-zone[data-type="menu_trigger"].active {
      background: transparent;
      transform: none;
      box-shadow: none;
    }

    /* Menu overlay — fade in/out */
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
    /* Card — slide down from top */
    .rb-menu-card {
      position: absolute;
      top: 0;
      left: 50%;
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
      transform: translate(-50%, -110%);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .rb-menu-overlay.open .rb-menu-card {
      transform: translate(-50%, 0);
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
# (reference copy — not used; see retrobox/statics.py)
# ---------------------------------------------------------------------------
_REMOVED_JS = r"""
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
      // Centred via CSS — no dynamic left/width needed
    }

    /* ── D-pad: axis-dominance + diagonal + neutral zone ────── */
    var dpadCenter  = null;   // screen {x,y} of dpad group centre
    var dpadRadius  = 0;      // half width of the full dpad bounding box (px)
    var dpadTouchId = null;   // identifier of the touch owning the dpad (null=idle)
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
      dpadCenter = { x:(minX+maxX)/2, y:(minY+maxY)/2 };
      dpadRadius = (maxX - minX) / 2;
    }

    function dpadDirsAt(cx, cy) {
      if (!dpadCenter) return [];
      var dx = cx - dpadCenter.x, dy = cy - dpadCenter.y;
      var dist = Math.hypot(dx, dy);
      if (dist < dpadRadius * DPAD_DEAD) return [];
      var nx = dx/dist, ny = dy/dist;
      var ax = Math.abs(nx), ay = Math.abs(ny);
      if (ax > DPAD_DIAG && ay > DPAD_DIAG)
        return [(nx>0?'right':'left'), (ny>0?'down':'up')];
      if (ax >= ay) return [nx>0?'right':'left'];
      return [ny>0?'down':'up'];
    }

    function applyDpadDirs(dirs) {
      var set = {}; for (var i=0; i<dirs.length; i++) set[dirs[i]] = true;
      var zones = touchLayer.querySelectorAll('.rb-zone[data-type="dpad"]');
      for (var i = 0; i < zones.length; i++) {
        var z = zones[i];
        var zd = (z.dataset.directions||'').split(',').filter(Boolean);
        var match = (zd.length===dirs.length) && zd.every(function(d){ return set[d]; });
        if (match) z.classList.add('active');
        else        z.classList.remove('active');
      }
    }

    /* ── Floating analog joystick ─────────────────────────── */
    var jsZone     = null;   // joystick zone element
    var jsKnob     = null;   // moving puck div
    var jsBase     = null;   // base ring div
    var jsTouchId  = null;   // touch identifier (null = idle)
    var jsAnchorX  = 0;      // float-centre x in zone coords (px from left)
    var jsAnchorY  = 0;      // float-centre y in zone coords (px from top)
    var jsMaxR     = 0;      // max travel radius (px)
    var jsTimer    = null;   // snap-back cleanup timer

    function prepareAnalog() {
      jsZone = document.querySelector('.rb-zone[data-type="joystick"]');
      if (!jsZone) return;
      jsKnob = jsZone.querySelector('.rb-joystick-knob');
      jsBase = jsZone.querySelector('.rb-joystick-base');
      _jsReset();
    }

    function _jsReset() {
      if (jsKnob) { jsKnob.classList.remove('dragging'); jsKnob.style.transform = ''; }
      if (jsBase) { jsBase.classList.remove('visible'); jsBase.style.cssText = ''; }
      jsAnchorX = 0; jsAnchorY = 0; jsMaxR = 0;
    }

    function jsActivate(cx, cy) {
      if (!jsZone) return;
      if (jsTimer) { clearTimeout(jsTimer); jsTimer = null; }
      var r = jsZone.getBoundingClientRect();
      jsMaxR = r.width * 0.34;
      // Fixed centre — always the zone centre, independent of where the finger lands
      jsAnchorX = r.width  / 2;
      jsAnchorY = r.height / 2;
      if (jsBase) {
        var sz = jsMaxR * 2;
        jsBase.style.left = (jsAnchorX - jsMaxR) + 'px';
        jsBase.style.top  = (jsAnchorY - jsMaxR) + 'px';
        jsBase.style.width  = sz + 'px';
        jsBase.style.height = sz + 'px';
        jsBase.classList.add('visible');
      }
      if (jsKnob) { jsKnob.classList.add('dragging'); _jsKnobTo(0, 0); }
    }

    function _jsKnobTo(dx, dy) {
      if (!jsKnob || !jsZone) return;
      var r = jsZone.getBoundingClientRect();
      var ox = jsAnchorX + dx - r.width  * 0.5;
      var oy = jsAnchorY + dy - r.height * 0.5;
      jsKnob.style.transform =
        'translate(calc(-50% + '+ox+'px), calc(-50% + '+oy+'px))';
    }

    function moveKnob(cx, cy) {
      if (!jsZone || !jsKnob || jsTouchId === null) return;
      var r  = jsZone.getBoundingClientRect();
      var dx = cx - r.left - jsAnchorX;
      var dy = cy - r.top  - jsAnchorY;
      var d  = Math.hypot(dx, dy);
      if (d > jsMaxR) { dx = dx/d*jsMaxR; dy = dy/d*jsMaxR; }
      _jsKnobTo(dx, dy);
    }

    function resetKnob() {
      if (!jsKnob) return;
      jsTouchId = null;
      jsKnob.classList.remove('dragging');  // re-enable CSS transition
      _jsKnobTo(0, 0);                      // ease back to float anchor
      if (jsTimer) clearTimeout(jsTimer);
      jsTimer = setTimeout(function() {     // then settle at zone centre
        jsTimer = null;
        _jsReset();
      }, 140);
    }

    window.addEventListener('load',   function() { positionZones(); prepareDpad(); prepareAnalog(); });
    window.addEventListener('resize', function() { positionZones(); prepareDpad(); prepareAnalog(); });

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

    /* release all inputs when the page is hidden (app switch etc.) */
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
        jsTouchId = -1;   // -1 = mouse sentinel
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


class ControllerGenerator:
    """Generates self-contained HTML controller UIs from a ControllerConfig."""

    def generate(self, config: ControllerConfig, output_dir: str) -> str:
        """Write index.html into *output_dir* and return the full path.

        The *output_dir* is also used when resolving asset paths such as the
        logo image; this allows us to look inside the console folder first and
        fall back to shared "base assets" if the file doesn't live there.
        """
        os.makedirs(output_dir, exist_ok=True)
        html = self._build_html(config, output_dir)
        path = os.path.join(output_dir, "index.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return path

    # ── private helpers ────────────────────────────────────────────────

    def _build_html(self, config: ControllerConfig, output_dir: str) -> str:
        css  = self._build_css(config)
        body = self._build_body(config, output_dir)
        js   = self._build_js(config)

        title = f"{config.brand_name} {config.name} Controller"

        return (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="UTF-8" />\n'
            '  <meta name="viewport" content="width=device-width, '
            'initial-scale=1.0, maximum-scale=1.0, user-scalable=no, '
            'viewport-fit=cover" />\n'
            f"  <title>{title}</title>\n"
            f"  <style>\n{css}\n  </style>\n"
            "</head>\n"
            f"{body}\n"
            "</html>\n"
        )

    def _build_css(self, config: ControllerConfig) -> str:
        return f"    :root {{ --rb-bg: {config.background_color}; }}\n" + _STATIC_CSS

    def _build_body(self, config: ControllerConfig, output_dir: str) -> str:
        svg_src   = quote(config.svg_filename)
        zones_el  = self._build_zones_html(config, output_dir)
        menu_el   = self._build_menu_html(config, output_dir)
        js        = self._build_js(config)

        return (
            "<body>\n"
            '  <div class="rb-container" id="rb-container">\n'
            f'    <img src="{svg_src}" class="rb-svg" '
            f'alt="{config.name} Controller" />\n'
            f'    <div class="rb-touch-layer" id="rb-touch-layer">\n'
            f'{zones_el}'
            '    </div>\n'
            '  </div>\n'
            f'{menu_el}'
            f'  <script>\n{js}\n  </script>\n'
            '</body>'
        )

    def _resolve_logo_src(self, config: ControllerConfig, output_dir: str) -> str:
        """Return a base64 data URI for the logo, or a quoted filename fallback."""
        if not config.logo_filename:
            return ""
        potential_paths = [
            os.path.join(output_dir, config.logo_filename),
            os.path.join(ROOT, "assets", config.logo_filename),
            os.path.join(ROOT, config.logo_filename),
        ]
        # Detect MIME type from file extension
        import mimetypes
        mime_type, _ = mimetypes.guess_type(config.logo_filename)
        if not mime_type:
            mime_type = "application/octet-stream"
        src = quote(config.logo_filename)
        for p in potential_paths:
            if os.path.isfile(p):
                try:
                    import base64
                    with open(p, "rb") as f:
                        data = f.read()
                    b64 = base64.b64encode(data).decode("ascii")
                    src = f"data:{mime_type};base64,{b64}"
                except Exception:
                    pass
                break
        return src

    def _build_zones_html(self, config: ControllerConfig, output_dir: str) -> str:
        logo_src = self._resolve_logo_src(config, output_dir)
        lines = []
        for z in config.touch_zones:
            dirs_attr = ""
            if z.directions:
                dirs_attr = f' data-directions="{",".join(z.directions)}"'
            if z.zone_type == ZoneType.JOYSTICK:
                lines.append(
                    f'      <div class="rb-zone" id="zone-{z.id}" '
                    f'data-type="{z.zone_type.value}" '
                    f'data-shape="{z.shape.value}"'
                    f'{dirs_attr}>'
                    f'<div class="rb-joystick-base"></div>'
                    f'<div class="rb-joystick-knob"></div></div>'
                )
            elif (
                z.zone_type == ZoneType.MENU_TRIGGER and logo_src
                and getattr(config, 'tab_logo_enabled', True)
            ):
                # allow per-controller scale override
                scale_pct = getattr(config, 'tab_logo_scale', 0.79) * 100
                offset = getattr(config, 'tab_logo_offset_y', 0.0)
                style_parts = []
                if scale_pct != 79:
                    style_parts.append(f'height:{scale_pct}%')
                if offset:
                    style_parts.append(f'transform:translateY({offset}px)')
                style_attr = (' style="' + ';'.join(style_parts) + '"') if style_parts else ''
                lines.append(
                    f'      <div class="rb-zone" id="zone-{z.id}" '
                    f'data-type="{z.zone_type.value}" '
                    f'data-shape="{z.shape.value}"'
                    f'{dirs_attr}>'
                    f'<img class="rb-tab-logo" src="{logo_src}"{style_attr} '
                    f'alt="{config.brand_name}" /></div>'
                )
            else:
                lines.append(
                    f'      <div class="rb-zone" id="zone-{z.id}" '
                    f'data-type="{z.zone_type.value}" '
                    f'data-shape="{z.shape.value}"'
                    f'{dirs_attr}></div>'
                )
        return "\n".join(lines) + "\n"

    def _build_menu_html(self, config: ControllerConfig, output_dir: str) -> str:
        if not config.menu_items:
            return ""

        items: list[str] = []
        for mi in config.menu_items:
            if mi.is_divider:
                items.append('      <div class="rb-menu-divider"></div>')
            else:
                items.append(
                    f'      <button class="rb-menu-item {mi.style}">'
                    f'{mi.label}</button>'
                )

        logo_html = ""
        if config.logo_filename:
            # Attempt to load the image file and embed it as a data URI.  First
            # look in the console output directory, then fall back to a
            # top‑level "assets" folder which may contain shared base assets.
            potential_paths = [
                os.path.join(output_dir, config.logo_filename),
                os.path.join(ROOT, "assets", config.logo_filename),
                os.path.join(ROOT, config.logo_filename),
            ]
            logo_src = quote(config.logo_filename)  # fallback URL
            for p in potential_paths:
                if os.path.isfile(p):
                    try:
                        import base64
                        with open(p, "rb") as f:
                            data = f.read()
                        b64 = base64.b64encode(data).decode("ascii")
                        logo_src = f"data:image/png;base64,{b64}"
                    except Exception:
                        # if reading fails, just keep the quote'd filename
                        pass
                    break

            logo_html = (
                f'      <div class="rb-menu-logo">\n'
                f'        <img src="{logo_src}" alt="{config.brand_name}" />\n'
                f'      </div>\n'
            )

        items_str = "\n".join(items)
        return (
            '  <div class="rb-menu-overlay" id="rb-menu-overlay">\n'
            '    <div class="rb-menu-card" id="rb-menu-card">\n'
            f'{items_str}\n'
            f'{logo_html}'
            '    </div>\n'
            '  </div>\n'
        )

    def _build_js(self, config: ControllerConfig) -> str:
        zones_json   = json.dumps([z.to_dict() for z in config.touch_zones], indent=2)
        key_map_json = json.dumps(config.keyboard_map, indent=2)

        dynamic = (
            f"    var SVG_W = {config.viewport_width};\n"
            f"    var SVG_H = {config.viewport_height};\n"
            f"    var ZONES = {zones_json};\n"
            f"    var KEY_MAP = {key_map_json};\n"
            f"    var DPAD_CARDINAL_ONLY = {'true' if config.dpad_cardinal_only else 'false'};\n"
        )
        return dynamic + _STATIC_JS
