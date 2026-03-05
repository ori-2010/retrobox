"""RetroBox FastAPI server.

Serves the phone-controller UIs and handles WebSocket connections that relay
button events to Linux virtual gamepads (uinput).

Endpoints
─────────
GET  /                         → redirect to /nes/
GET  /{console}/               → serve the generated controller index.html
GET  /{console}/{filename}     → serve static assets inside the console folder
     (SVG, fonts, images …)
WS   /ws                       → phone controller connection

WebSocket protocol (client → server)
──────────────────────────────────────
  { "button": "<zone-id>", "state": "down"|"up" }
  { "type": "menu_action", "action": "shutdown"|"disconnect"|"close_game" }

WebSocket protocol (server → client)
──────────────────────────────────────
  { "type": "assign",        "player": <1‑4> }
  { "type": "reassign",      "player": <1‑4> }
  { "type": "full",          "message": "Lobby full" }
  { "type": "console_change","console": "<name>" }

Environment / configuration
────────────────────────────
  RETROBOX_ROOT   path that contains nes/, gba/, psp/ (default: repo root)
  RETROBOX_MAX_PLAYERS   integer, default 4
  RETROBOX_CONSOLE       active console name shown on new connections (default: nes)

Run with:
    uvicorn server.server:app --host 0.0.0.0 --port 80
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

# ── paths ─────────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent          # retrobox/server/
ROOT  = Path(os.environ.get("RETROBOX_ROOT", str(_HERE.parent)))

# ── configuration ─────────────────────────────────────────────────────────────
MAX_PLAYERS: int     = int(os.environ.get("RETROBOX_MAX_PLAYERS", "4"))
ACTIVE_CONSOLE: str  = os.environ.get("RETROBOX_CONSOLE", "nes")

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("retrobox.server")

# ── optional evdev import ─────────────────────────────────────────────────────
try:
    from server.gamepad import create_gamepad, write_event, destroy_gamepad
    _EVDEV_AVAILABLE = True
except Exception:
    _EVDEV_AVAILABLE = False
    log.warning(
        "python-evdev not available — virtual gamepad support is disabled. "
        "Button events will be logged but not forwarded to uinput."
    )


# ── player / lobby state ──────────────────────────────────────────────────────

class PlayerSlot:
    """Holds one connected phone-controller's WebSocket and its virtual gamepad."""

    def __init__(self, player: int, ws: WebSocket):
        self.player   = player
        self.ws       = ws
        self.gamepad  = None  # evdev.UInput | None

    async def send(self, msg: dict) -> None:
        try:
            await self.ws.send_text(json.dumps(msg))
        except Exception:
            pass  # connection may have already closed

    def create_gamepad(self) -> None:
        if _EVDEV_AVAILABLE:
            try:
                self.gamepad = create_gamepad(self.player)
            except Exception as exc:
                log.warning("Could not create gamepad for P%d: %s", self.player, exc)

    def destroy_gamepad(self) -> None:
        if self.gamepad is not None:
            try:
                destroy_gamepad(self.gamepad)
            except Exception:
                pass
            self.gamepad = None


class Lobby:
    """Manages up to MAX_PLAYERS concurrent phone-controller connections."""

    def __init__(self) -> None:
        # slot index 0 → player 1, …, index (MAX_PLAYERS-1) → player MAX_PLAYERS
        self._slots: list[Optional[PlayerSlot]] = [None] * MAX_PLAYERS
        self._lock = asyncio.Lock()
        self._console = ACTIVE_CONSOLE

    # ── joining / leaving ─────────────────────────────────────────────────────

    async def join(self, ws: WebSocket) -> Optional[PlayerSlot]:
        async with self._lock:
            for i, slot in enumerate(self._slots):
                if slot is None:
                    player = i + 1
                    ps     = PlayerSlot(player, ws)
                    ps.create_gamepad()
                    self._slots[i] = ps
                    log.info("P%d joined", player)
                    return ps
        return None  # lobby full

    async def leave(self, ps: PlayerSlot) -> None:
        async with self._lock:
            idx = ps.player - 1
            if 0 <= idx < len(self._slots) and self._slots[idx] is ps:
                self._slots[idx] = None
            ps.destroy_gamepad()
        log.info("P%d left", ps.player)

    async def broadcast(self, msg: dict) -> None:
        """Send a message to every connected player."""
        async with self._lock:
            active = [s for s in self._slots if s is not None]
        for slot in active:
            await slot.send(msg)

    # ── console switching ─────────────────────────────────────────────────────

    async def switch_console(self, console: str) -> None:
        """Switch the active console and notify all connected controllers."""
        self._console = console
        log.info("Console switched to %s", console)
        await self.broadcast({"type": "console_change", "console": console})

    @property
    def console(self) -> str:
        return self._console


lobby = Lobby()

# ── FastAPI app ────────────────────────────────────────────────────────────────

app = FastAPI(title="RetroBox Server", version="0.1.0")


# ── HTTP routes ───────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    return RedirectResponse(url=f"/{lobby.console}/")


@app.get("/{console}/", response_model=None, include_in_schema=False)
async def console_index(console: str) -> FileResponse | HTMLResponse:
    """Serve the generated index.html for the requested console."""
    path = ROOT / console / "index.html"
    if path.is_file():
        return FileResponse(str(path), media_type="text/html")
    return HTMLResponse(
        f"<h1>Console '{console}' not found</h1>"
        f"<p>Generate it first: <code>python generate.py {console}</code></p>",
        status_code=404,
    )


@app.get("/{console}/{filename:path}", response_model=None, include_in_schema=False)
async def console_asset(console: str, filename: str) -> FileResponse | HTMLResponse:
    """Serve a static asset (SVG, font, image) from the console's folder.

    Path traversal is prevented by resolving the full path and ensuring it
    stays within ROOT / console before the file is served.
    """
    console_dir = (ROOT / console).resolve()
    asset_path  = (console_dir / filename).resolve()
    # Reject any path that escapes the console directory
    if not str(asset_path).startswith(str(console_dir) + os.sep) and \
            asset_path != console_dir:
        return HTMLResponse("<h1>Forbidden</h1>", status_code=403)
    if asset_path.is_file():
        return FileResponse(str(asset_path))
    return HTMLResponse(f"<h1>Not found: {console}/{filename}</h1>", status_code=404)


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def ws_controller(websocket: WebSocket) -> None:
    """Handle a phone-controller connection."""
    await websocket.accept()

    ps = await lobby.join(websocket)
    if ps is None:
        await websocket.send_text(
            json.dumps({"type": "full", "message": "Lobby full"})
        )
        await websocket.close()
        return

    await ps.send({"type": "assign", "player": ps.player})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if "button" in msg:
                _handle_button(ps, msg)
            elif msg.get("type") == "menu_action":
                await _handle_menu_action(ps, msg.get("action", ""))

    except WebSocketDisconnect:
        pass
    finally:
        await lobby.leave(ps)


# ── message handlers ──────────────────────────────────────────────────────────

def _handle_button(ps: PlayerSlot, msg: dict) -> None:
    zone_id = str(msg.get("button", ""))
    state   = str(msg.get("state",  "up"))
    log.debug("P%d  %s  %s", ps.player, zone_id, state)
    if ps.gamepad is not None and _EVDEV_AVAILABLE:
        try:
            write_event(ps.gamepad, zone_id, state)
        except Exception as exc:
            log.warning("gamepad write error (P%d): %s", ps.player, exc)


async def _handle_menu_action(ps: PlayerSlot, action: str) -> None:
    log.info("P%d menu action: %s", ps.player, action)
    if action == "disconnect":
        # Notify the client before freeing the slot so the message is delivered
        await ps.send({"type": "assign", "player": 0})
        await lobby.leave(ps)
    elif action == "shutdown":
        log.info("Shutdown requested by P%d", ps.player)
        asyncio.create_task(_shutdown())
    elif action == "close_game":
        log.info("Close game requested by P%d", ps.player)
        asyncio.create_task(_close_game())


async def _shutdown() -> None:
    """Gracefully shut down the host machine.

    Requires passwordless sudo for 'shutdown' in /etc/sudoers, e.g.:
        retrobox ALL=(ALL) NOPASSWD: /sbin/shutdown
    """
    await asyncio.sleep(0.5)
    try:
        subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
    except Exception as exc:
        log.error("Shutdown failed: %s", exc)


async def _close_game() -> None:
    """Ask RetroArch (or any full-screen window) to quit."""
    await asyncio.sleep(0.1)
    try:
        # send SIGTERM to RetroArch if it is running
        subprocess.run(["pkill", "-SIGTERM", "retroarch"], check=False)
    except Exception as exc:
        log.error("Close game failed: %s", exc)


# ── admin API (localhost only) ────────────────────────────────────────────────

_LOCALHOST = {"127.0.0.1", "::1"}


@app.post("/admin/console/{console}", include_in_schema=False)
async def admin_switch_console(console: str, request: Request) -> dict:
    """Switch the active console (callable from localhost scripts only)."""
    client_host = request.client.host if request.client else ""
    if client_host not in _LOCALHOST:
        return HTMLResponse("<h1>Forbidden</h1>", status_code=403)
    await lobby.switch_console(console)
    return {"ok": True, "console": console}


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry-point for `retrobox-server` console script."""
    import uvicorn
    uvicorn.run("server.server:app", host="0.0.0.0", port=80, reload=False)


if __name__ == "__main__":
    main()
