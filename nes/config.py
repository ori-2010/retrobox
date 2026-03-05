#!/usr/bin/env python3
"""NES controller configuration for RetroBox.

Run via:  python generate.py nes
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrobox import ControllerConfig, TouchZone, MenuItem, ZoneType, ZoneShape


def get_config() -> ControllerConfig:
    # D-pad 3×3 grid matching the SVG d-pad area  (x=57 y=136 w=201 h=201)
    DX, DY = 57, 136
    C = 67                         # cell size  (201 / 3)

    return ControllerConfig(
        name="NES",
        svg_filename="iPhone 13 & 14 - 1.svg",
        logo_filename="retrobox full logo.svg",
        tab_logo_enabled=False,
        tab_logo_scale=0.79,
        tab_logo_offset_y=0.0,
        viewport_width=844,
        viewport_height=390,
        background_color="#000000",
        brand_name="RetroBox",

        touch_zones=[
            # ── D-pad 3×3 grid ──────────────────────────────────
            TouchZone("dpad-up-left",    DX,        DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, ["up", "left"]),
            TouchZone("dpad-up",         DX + C,    DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, ["up"]),
            TouchZone("dpad-up-right",   DX + 2*C,  DY,        C, C, ZoneType.DPAD, ZoneShape.RECT, ["up", "right"]),
            TouchZone("dpad-left",       DX,        DY + C,    C, C, ZoneType.DPAD, ZoneShape.RECT, ["left"]),
            TouchZone("dpad-right",      DX + 2*C,  DY + C,    C, C, ZoneType.DPAD, ZoneShape.RECT, ["right"]),
            TouchZone("dpad-down-left",  DX,        DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, ["down", "left"]),
            TouchZone("dpad-down",       DX + C,    DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, ["down"]),
            TouchZone("dpad-down-right", DX + 2*C,  DY + 2*C,  C, C, ZoneType.DPAD, ZoneShape.RECT, ["down", "right"]),

            # ── SELECT / START  (expanded touch targets) ────────
            TouchZone("btn-select", 336, 268, 76, 52, ZoneType.BUTTON, ZoneShape.PILL),
            TouchZone("btn-start",  432, 268, 76, 52, ZoneType.BUTTON, ZoneShape.PILL),

            # ── A / B buttons  (gray plate area for bigger targets)
            TouchZone("btn-b", 566, 244, 100, 100, ZoneType.BUTTON, ZoneShape.ROUND),
            TouchZone("btn-a", 695, 244, 100, 100, ZoneType.BUTTON, ZoneShape.ROUND),

            # ── Menu trigger  (logo tab at top of controller) ───
            TouchZone("menu-trigger", 358, 0, 126, 43, ZoneType.MENU_TRIGGER, ZoneShape.RECT),
        ],

        menu_items=[
            MenuItem("Turn Off Console",      "danger"),
            MenuItem("Disconnect controller", "danger"),
            MenuItem.divider(),
            MenuItem("Close Game",            "default"),
        ],

        keyboard_map={
            "ArrowUp":    "dpad-up",
            "ArrowDown":  "dpad-down",
            "ArrowLeft":  "dpad-left",
            "ArrowRight": "dpad-right",
            "z": "btn-b",  "Z": "btn-b",
            "x": "btn-a",  "X": "btn-a",
            " ": "btn-select",
            "Enter": "btn-start",
        },
    )
