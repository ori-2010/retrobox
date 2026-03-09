#!/usr/bin/env python3
"""PSP controller configuration for RetroBox.

Run via:  python generate.py psp
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrobox import ControllerConfig, TouchZone, MenuItem, ZoneType, ZoneShape


def get_config() -> ControllerConfig:
    # ── D-pad 3×3 grid ──────────────────────────────────────────────
    # D-pad area: circle centered at (166, 191) with r=101
    # Grid spans from (65, 90) to (267, 293)
    DX, DY = 65, 90    # top-left of 3×3 grid
    C = 67             # cell size (202 / 3)

    # ── Action button cluster ────────────────────────────────────────
    # Circle centered at (686, 193), r=89.5
    # Button centers: △(686,113) □(600,193) ○(769,193) ✕(686,274)

    return ControllerConfig(
        name="PSP",
        svg_filename="psp_controller.svg",
        logo_filename="retrobox full logo.svg",
        tab_logo_enabled=True,
        tab_logo_scale=0.79,
        tab_logo_offset_y=0.0,
        viewport_width=844,
        viewport_height=390,
        # controllers render on a phone; always use pure black background
        background_color="#000000",
        brand_name="RetroBox",

        touch_zones=[
            # ── L / R shoulder buttons ──────────────────────────────
            TouchZone("btn-l",   39,   3, 254, 35, ZoneType.BUTTON, ZoneShape.PILL),
            TouchZone("btn-r",  552,   3, 256, 37, ZoneType.BUTTON, ZoneShape.PILL),

            # ── Menu trigger (RetroBox logo — wider touch zone) ─────
            TouchZone("menu-trigger", 310, 0, 224, 50, ZoneType.MENU_TRIGGER, ZoneShape.RECT),

            # ── D-pad 3×3 grid (with diagonals) ────────────────────
            TouchZone("dpad-up-left",    DX,        DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, ["up",   "left"]),
            TouchZone("dpad-up",         DX + C,    DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, ["up"]),
            TouchZone("dpad-up-right",   DX + 2*C,  DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, ["up",   "right"]),
            TouchZone("dpad-left",       DX,        DY + C,    C, C, ZoneType.DPAD, ZoneShape.RECT, ["left"]),
            TouchZone("dpad-right",      DX + 2*C,  DY + C,    C, C, ZoneType.DPAD, ZoneShape.RECT, ["right"]),
            TouchZone("dpad-down-left",  DX,        DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, ["down", "left"]),
            TouchZone("dpad-down",       DX + C,    DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, ["down"]),
            TouchZone("dpad-down-right", DX + 2*C,  DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, ["down", "right"]),

            # ── Analog stick (center 325, 329) ──────────────────────
            TouchZone("analog-stick", 260, 264, 130, 130, ZoneType.JOYSTICK, ZoneShape.ROUND),

            # ── Action face buttons (bigger 80×80 hit areas) ────────
            TouchZone("btn-triangle", 644,  71, 80, 80, ZoneType.BUTTON, ZoneShape.ROUND),
            TouchZone("btn-square",   558, 151, 80, 80, ZoneType.BUTTON, ZoneShape.ROUND),
            TouchZone("btn-circle",   727, 151, 80, 80, ZoneType.BUTTON, ZoneShape.ROUND),
            TouchZone("btn-cross",    644, 232, 80, 80, ZoneType.BUTTON, ZoneShape.ROUND),

            # ── Select / Start (matching SVG rects precisely) ────────
            TouchZone("btn-select", 526, 340, 120, 40, ZoneType.BUTTON, ZoneShape.PILL),
            TouchZone("btn-start",  635, 340, 120, 40, ZoneType.BUTTON, ZoneShape.PILL),
        ],

        menu_items=[
            MenuItem("Turn Off Console",      "danger"),
            MenuItem("Disconnect controller", "danger"),
            MenuItem.divider(),
            MenuItem("Close Game",            "default"),
        ],

        keyboard_map={
            # D-pad
            "ArrowUp":    "dpad-up",
            "ArrowDown":  "dpad-down",
            "ArrowLeft":  "dpad-left",
            "ArrowRight": "dpad-right",
            # Face buttons  (PSP layout: ▲ □ ○ ✕)
            "i": "btn-triangle", "I": "btn-triangle",
            "j": "btn-square",   "J": "btn-square",
            "l": "btn-circle",   "L": "btn-circle",
            "x": "btn-cross",    "X": "btn-cross",
            # Shoulder
            "q": "btn-l",        "Q": "btn-l",
            "e": "btn-r",        "E": "btn-r",
            # Menu
            " ": "btn-select",
            "Enter": "btn-start",
        },
    )
