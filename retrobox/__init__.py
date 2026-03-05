"""RetroBox Controller Generator — reusable toolkit for virtual controller UIs."""

from .models import ControllerConfig, TouchZone, MenuItem, ZoneType, ZoneShape
from .generator import ControllerGenerator
from .statics import STATIC_CSS, STATIC_JS

__all__ = [
    "ControllerConfig",
    "TouchZone",
    "MenuItem",
    "ZoneType",
    "ZoneShape",
    "ControllerGenerator",
    # Shared static assets — import these in any custom controller pipeline:
    #   from retrobox import STATIC_CSS, STATIC_JS
    "STATIC_CSS",
    "STATIC_JS",
]
