"""WebSocket client JS for RetroBox server-connected mode.

Injected after STATIC_JS when ControllerConfig.websocket_enabled is True.
Hooks into the existing activate/deactivate and applyDpadDirs functions
to send button events over WebSocket, and handles incoming server messages
(player assignment, reassignment, lobby full, console change).

    from retrobox.ws_client import WEBSOCKET_JS
"""

WEBSOCKET_JS = r"""
    /* ── RetroBox WebSocket client ────────────────────────── */
    (function() {
      var ws = null;
      var playerNum = null;
      var reconnectDelay = 200;
      var MAX_RECONNECT = 5000;
      var prevDpadDirs = [];
      var fullscreenDone = false;

      /* ── connection status dot ─────────────────────────── */
      var dot = document.createElement('div');
      dot.id = 'rb-ws-dot';
      dot.style.cssText =
        'position:fixed;bottom:8px;right:8px;width:10px;height:10px;' +
        'border-radius:50%;background:#d32f2f;z-index:200;' +
        'transition:background 0.3s;pointer-events:none;';
      document.body.appendChild(dot);

      /* ── player badge ──────────────────────────────────── */
      var badge = document.createElement('div');
      badge.id = 'rb-player-badge';
      badge.style.cssText =
        'position:fixed;top:8px;left:8px;padding:2px 10px;' +
        'border-radius:12px;background:rgba(255,255,255,0.15);' +
        'color:#fff;font:bold 13px/18px -apple-system,BlinkMacSystemFont,' +
        '"Segoe UI",sans-serif;z-index:200;pointer-events:none;' +
        'opacity:0;transition:opacity 0.3s;';
      document.body.appendChild(badge);

      function showBadge(p) {
        playerNum = p;
        badge.textContent = 'P' + p;
        badge.style.opacity = '1';
      }

      /* ── fullscreen + landscape on first touch ─────────── */
      function tryFullscreen() {
        if (fullscreenDone) return;
        fullscreenDone = true;
        try {
          var el = document.documentElement;
          if (el.requestFullscreen) el.requestFullscreen();
          else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
        } catch(e) {}
        try {
          if (screen.orientation && screen.orientation.lock)
            screen.orientation.lock('landscape').catch(function(){});
        } catch(e) {}
      }
      document.addEventListener('touchstart', tryFullscreen, { once: true });

      /* ── wrap activate / deactivate for button zones ───── */
      var _origActivate = activate;
      var _origDeactivate = deactivate;

      activate = function(el) {
        _origActivate(el);
        var t = el.dataset.type;
        if (t === 'button') {
          sendBtn(el.id.replace('zone-', ''), 'down');
          vibrate();
        } else if (t === 'menu_trigger') {
          // menu_trigger handled by original code
        }
      };

      deactivate = function(el) {
        _origDeactivate(el);
        var t = el.dataset.type;
        if (t === 'button') {
          sendBtn(el.id.replace('zone-', ''), 'up');
        }
      };

      /* ── wrap applyDpadDirs to diff direction changes ──── */
      var _origApplyDpad = applyDpadDirs;
      applyDpadDirs = function(dirs) {
        _origApplyDpad(dirs);
        // diff against previous state
        var oldSet = {};
        for (var i = 0; i < prevDpadDirs.length; i++) oldSet[prevDpadDirs[i]] = true;
        var newSet = {};
        for (var i = 0; i < dirs.length; i++) newSet[dirs[i]] = true;
        // newly pressed directions
        for (var i = 0; i < dirs.length; i++) {
          if (!oldSet[dirs[i]]) {
            sendBtn('dpad-' + dirs[i], 'down');
            vibrate();
          }
        }
        // released directions
        for (var i = 0; i < prevDpadDirs.length; i++) {
          if (!newSet[prevDpadDirs[i]]) {
            sendBtn('dpad-' + prevDpadDirs[i], 'up');
          }
        }
        prevDpadDirs = dirs.slice();
      };

      /* ── vibration ─────────────────────────────────────── */
      function vibrate() {
        if (navigator.vibrate) navigator.vibrate(30);
      }

      /* ── send button event ─────────────────────────────── */
      function sendBtn(zoneId, state) {
        if (ws && ws.readyState === 1) {
          ws.send(JSON.stringify({ button: zoneId, state: state }));
        }
      }

      /* ── menu item interception ────────────────────────── */
      var menuActions = {
        'Turn Off Console': 'shutdown',
        'Disconnect controller': 'disconnect',
        'Close Game': 'close_game'
      };
      var mc = document.getElementById('rb-menu-card');
      if (mc) {
        mc.addEventListener('click', function(e) {
          if (e.target.classList.contains('rb-menu-item')) {
            var label = e.target.textContent.trim();
            var action = menuActions[label];
            if (action && ws && ws.readyState === 1) {
              ws.send(JSON.stringify({ type: 'menu_action', action: action }));
            }
          }
        });
      }

      /* ── WebSocket connection ──────────────────────────── */
      function connect() {
        var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        var url = proto + '//' + location.host + '/ws';
        ws = new WebSocket(url);

        ws.onopen = function() {
          dot.style.background = '#4caf50';
          reconnectDelay = 200;
        };

        ws.onmessage = function(e) {
          var msg;
          try { msg = JSON.parse(e.data); } catch(err) { return; }

          if (msg.type === 'assign') {
            showBadge(msg.player);
          } else if (msg.type === 'reassign') {
            showBadge(msg.player);
          } else if (msg.type === 'full') {
            badge.textContent = msg.message || 'Lobby full';
            badge.style.opacity = '1';
            badge.style.background = 'rgba(211,47,47,0.6)';
          } else if (msg.type === 'console_change') {
            window.location.href = '/' + msg.console + '/';
          }
        };

        ws.onclose = function() {
          dot.style.background = '#d32f2f';
          scheduleReconnect();
        };

        ws.onerror = function() {
          // onclose will fire after this
        };
      }

      function scheduleReconnect() {
        setTimeout(function() {
          reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT);
          connect();
        }, reconnectDelay);
      }

      /* ── release all on visibility hidden (extends existing handler) */
      document.addEventListener('visibilitychange', function() {
        if (document.hidden) prevDpadDirs = [];
      });

      /* ── start ─────────────────────────────────────────── */
      connect();
    })();
"""
