"""Virtual gamepad manager using python-evdev / uinput.

Creates Linux virtual gamepads that RetroArch recognises as Xbox 360
controllers (vendor 0x045e, product 0x028e) for automatic mapping.

Usage:
    gp = create_gamepad(player=1)
    write_event(gp, "btn-a", "down")
    write_event(gp, "dpad-up", "down")
    destroy_gamepad(gp)
"""

from __future__ import annotations

import logging

from evdev import UInput, ecodes, AbsInfo

log = logging.getLogger(__name__)

# Xbox 360 IDs — RetroArch auto-detects these without manual autoconfig.
_VENDOR = 0x045E
_PRODUCT = 0x028E

# NES button capabilities registered on every virtual gamepad.
_KEY_CAPS = [
    ecodes.BTN_SOUTH,   # B
    ecodes.BTN_EAST,    # A
    ecodes.BTN_START,
    ecodes.BTN_SELECT,
]

_ABS_CAPS = [
    (ecodes.ABS_HAT0X, AbsInfo(0, -1, 1, 0, 0, 0)),
    (ecodes.ABS_HAT0Y, AbsInfo(0, -1, 1, 0, 0, 0)),
]

_CAPABILITIES = {
    ecodes.EV_KEY: _KEY_CAPS,
    ecodes.EV_ABS: _ABS_CAPS,
}

# Zone-ID → (event_type, event_code, press_value, release_value)
_BUTTON_MAP: dict[str, tuple[int, int, int, int]] = {
    "btn-a":      (ecodes.EV_KEY, ecodes.BTN_EAST,   1, 0),
    "btn-b":      (ecodes.EV_KEY, ecodes.BTN_SOUTH,  1, 0),
    "btn-start":  (ecodes.EV_KEY, ecodes.BTN_START,  1, 0),
    "btn-select": (ecodes.EV_KEY, ecodes.BTN_SELECT, 1, 0),
    "dpad-up":    (ecodes.EV_ABS, ecodes.ABS_HAT0Y, -1, 0),
    "dpad-down":  (ecodes.EV_ABS, ecodes.ABS_HAT0Y,  1, 0),
    "dpad-left":  (ecodes.EV_ABS, ecodes.ABS_HAT0X, -1, 0),
    "dpad-right": (ecodes.EV_ABS, ecodes.ABS_HAT0X,  1, 0),
}


def create_gamepad(player: int) -> UInput:
    """Create a virtual gamepad for the given player number (1-based)."""
    name = f"RetroBox-P{player}"
    try:
        gp = UInput(
            _CAPABILITIES,
            name=name,
            vendor=_VENDOR,
            product=_PRODUCT,
        )
    except PermissionError:
        log.error(
            "Cannot create uinput device — permission denied. "
            "Run: sudo usermod -aG input $USER  then log out and back in, "
            "or create a udev rule for /dev/uinput."
        )
        raise
    log.info("Created virtual gamepad %s → %s", name, gp.device.path)
    return gp


def write_event(gamepad: UInput, zone_id: str, state: str) -> None:
    """Translate a zone-id + state ("down"/"up") into a uinput event."""
    mapping = _BUTTON_MAP.get(zone_id)
    if mapping is None:
        return
    ev_type, ev_code, press_val, release_val = mapping
    value = press_val if state == "down" else release_val
    gamepad.write(ev_type, ev_code, value)
    gamepad.syn()


def destroy_gamepad(gamepad: UInput) -> None:
    """Close and destroy a virtual gamepad."""
    try:
        path = gamepad.device.path
        gamepad.close()
        log.info("Destroyed virtual gamepad %s", path)
    except Exception:
        log.exception("Error destroying gamepad")
