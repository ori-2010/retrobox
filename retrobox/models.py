"""Data models for RetroBox controller definitions."""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class ZoneType(str, Enum):
    """Type of interactive touch zone."""
    DPAD = "dpad"
    BUTTON = "button"
    JOYSTICK = "joystick"
    MENU_TRIGGER = "menu_trigger"


class ZoneShape(str, Enum):
    """Visual shape of a touch zone (affects active-state border-radius)."""
    RECT = "rect"
    ROUND = "round"
    PILL = "pill"


@dataclass
class TouchZone:
    """An interactive touch zone overlaid on the controller SVG.

    Coordinates are in SVG viewport units (matching the source SVG).
    The generator scales them to match the rendered SVG at runtime.
    """
    id: str
    x: float
    y: float
    width: float
    height: float
    zone_type: ZoneType = ZoneType.BUTTON
    shape: ZoneShape = ZoneShape.RECT
    directions: List[str] = field(default_factory=list)
    rotation: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "w": self.width,
            "h": self.height,
            "type": self.zone_type.value,
            "shape": self.shape.value,
            "directions": self.directions,
            "rotation": self.rotation,
        }


@dataclass
class MenuItem:
    """An item in the controller overlay menu."""
    label: str = ""
    style: str = "default"      # "danger" (red) or "default" (dark)
    is_divider: bool = False

    @classmethod
    def divider(cls) -> "MenuItem":
        return cls(is_divider=True)


@dataclass
class ControllerConfig:
    """Full configuration for a console controller UI.

    Attributes:
        name:             Console name (e.g. "NES", "SNES", "Genesis").
        svg_filename:     Filename of the controller SVG in the output dir.
        logo_filename:    Filename of the brand logo image (optional).
        viewport_width:   SVG viewBox width.
        viewport_height:  SVG viewBox height.
        background_color: Page background colour.
        brand_name:       Brand name shown in menu footer.
        touch_zones:      List of interactive touch zones.
        menu_items:       Items for the overlay menu (empty = no menu).
        keyboard_map:     Mapping of KeyboardEvent.key → zone id.
    """
    name: str
    svg_filename: str
    logo_filename: str = ""
    viewport_width: int = 844
    viewport_height: int = 390
    background_color: str = "#000000"
    brand_name: str = "RetroBox"
    touch_zones: List[TouchZone] = field(default_factory=list)
    menu_items: List[MenuItem] = field(default_factory=list)
    keyboard_map: Dict[str, str] = field(default_factory=dict)
    # whether to render the logo inside the menu-trigger tab; some SVGs (NES)
    # already include a logo graphic so a second overlay would be redundant.
    tab_logo_enabled: bool = True
    # fraction of the zone height the tab logo should occupy (0–1)
    # when `tab_logo_enabled` is true.  The default is 0.79 (79%).
    tab_logo_scale: float = 0.79
    # additional vertical offset (px) applied to the tab logo image; positive moves down
    tab_logo_offset_y: float = 0.0
    # when True, the d-pad only registers cardinal directions (no diagonals)
    dpad_cardinal_only: bool = False
