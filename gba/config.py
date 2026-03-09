#!/usr/bin/env python3
"""GBA controller configuration for RetroBox.

Run via:  python generate.py gba
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrobox import ControllerConfig, TouchZone, MenuItem, ZoneType, ZoneShape


def get_config() -> ControllerConfig:
    # ── D-pad 3×3 grid ──────────────────────────────────────────────
    # D-pad SVG at (95, 98), size 234×234.  Corner zones provide touch
    # coverage but have no directions (never activate visually).
    DX, DY = 95, 98
    C = 78              # cell size (234 / 3)

    return ControllerConfig(
        name="GBA",
        svg_filename="gba_controller.svg",
        logo_filename="retrobox full logo.svg",
        tab_logo_enabled=True,
        tab_logo_scale=0.79,
        tab_logo_offset_y=0.0,
        viewport_width=844,
        viewport_height=390,
        background_color="#000000",
        brand_name="RetroBox",
        dpad_cardinal_only=True,

        touch_zones=[
            # ── L / R shoulder buttons ──────────────────────────────
            TouchZone("btn-l",   0, 40, 358, 35, ZoneType.BUTTON, ZoneShape.PILL),
            TouchZone("btn-r", 484, 40, 360, 35, ZoneType.BUTTON, ZoneShape.PILL),

            # ── Menu trigger (RetroBox logo tab — wider touch zone) ─
            TouchZone("menu-trigger", 310, 0, 224, 50, ZoneType.MENU_TRIGGER, ZoneShape.RECT),

            # ── D-pad 3×3 grid (cardinal-only with corner coverage) ─
            TouchZone("dpad-ul",    DX,        DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, []),
            TouchZone("dpad-up",    DX + C,    DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, ["up"]),
            TouchZone("dpad-ur",    DX + 2*C,  DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, []),
            TouchZone("dpad-left",  DX,        DY + C,    C, C, ZoneType.DPAD, ZoneShape.RECT, ["left"]),
            TouchZone("dpad-right", DX + 2*C,  DY + C,    C, C, ZoneType.DPAD, ZoneShape.RECT, ["right"]),
            TouchZone("dpad-dl",    DX,        DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, []),
            TouchZone("dpad-down",  DX + C,    DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, ["down"]),
            TouchZone("dpad-dr",    DX + 2*C,  DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, []),

            # ── A / B buttons (centered on SVG: A@(710,125,100×100) B@(608,215,100×100))
            TouchZone("btn-a", 705, 120, 110, 110, ZoneType.BUTTON, ZoneShape.ROUND),
            TouchZone("btn-b", 603, 210, 110, 110, ZoneType.BUTTON, ZoneShape.ROUND),

            # ── Start / Select (centered on SVG containers, rotated 20°) ─
            TouchZone("btn-start",  407, 278, 113, 40, ZoneType.BUTTON, ZoneShape.PILL, rotation=20.0),
            TouchZone("btn-select", 416, 317, 113, 40, ZoneType.BUTTON, ZoneShape.PILL, rotation=20.0),
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
            # Face buttons (GBA: A right, B left)
            "z": "btn-b",  "Z": "btn-b",
            "x": "btn-a",  "X": "btn-a",
            # Shoulder
            "q": "btn-l",  "Q": "btn-l",
            "e": "btn-r",  "E": "btn-r",
            # Menu
            " ": "btn-select",
            "Enter": "btn-start",
        },
    )
