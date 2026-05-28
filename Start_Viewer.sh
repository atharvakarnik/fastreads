#!/bin/bash
set -e

cd "$(dirname "$0")"

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"

URL="http://127.0.0.1:8000/viewer.html"
RUN_URL="${URL}?v=$(date +%s)"
SERVER_PID=""

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python 3.10+ is required but no Python interpreter was found."
  exit 1
fi

if ! "$PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "Python 3.10+ is required."
  "$PY" --version 2>/dev/null || true
  exit 1
fi

viewer_is_ready() {
  "$PY" - "$URL" <<'PY'
import sys
import urllib.request

url = sys.argv[1]
try:
    with urllib.request.urlopen(url, timeout=1) as response:
        content = response.read().decode("utf-8", errors="replace")
        ok = (
            response.status == 200
            and "petWindowSlider" in content
            and "centiloidReveal" in content
            and "crosshairToggle" in content
        )
        raise SystemExit(0 if ok else 1)
except Exception:
    raise SystemExit(1)
PY
}

port_is_available() {
  "$PY" - <<'PY'
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(("127.0.0.1", 8000))
except OSError:
    raise SystemExit(1)
finally:
    sock.close()
raise SystemExit(0)
PY
}

open_viewer() {
  if [ "${NO_BROWSER:-0}" = "1" ]; then
    echo "NO_BROWSER=1 set; not opening a browser automatically."
    return 0
  fi

  case "$(uname -s)" in
    Darwin)
      open "$RUN_URL"
      return 0
      ;;
    Linux)
      if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
        if command -v xdg-open >/dev/null 2>&1; then
          xdg-open "$RUN_URL" >/dev/null 2>&1 &
          return 0
        fi
        if command -v gio >/dev/null 2>&1; then
          gio open "$RUN_URL" >/dev/null 2>&1 &
          return 0
        fi
        if command -v firefox >/dev/null 2>&1; then
          firefox "$RUN_URL" >/dev/null 2>&1 &
          return 0
        fi
      fi
      ;;
  esac

  echo "Open this URL in a browser:"
  echo "  $RUN_URL"
  return 0
}

cleanup() {
  if [ -n "$SERVER_PID" ]; then
    echo ""
    echo "Stopping PET Viewer server..."
    kill "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if viewer_is_ready; then
  echo "PET Viewer server is already running at:"
  echo "  $URL"
  echo "Reusing the existing server."
elif ! port_is_available; then
  echo "Port 8000 is already in use, but it is not serving the current PET Viewer UI."
  echo "Close any old PET Viewer server windows/processes and try again."
  exit 1
else
  echo "Starting PET Viewer server..."
  "$PY" server.py &
  SERVER_PID=$!

  echo "Waiting for server..."
  deadline=$((SECONDS + 15))
  while ! viewer_is_ready; do
    if [ "$SECONDS" -ge "$deadline" ]; then
      echo "Server did not become ready at $URL"
      exit 1
    fi
    sleep 0.25
  done
fi

echo "Opening viewer..."
open_viewer

echo ""
echo "PET Viewer started at:"
echo "  $RUN_URL"
echo ""
if [ -n "$SERVER_PID" ]; then
  echo "Keep this Terminal window open while using the viewer."
  echo "Press Ctrl+C here when done."
  echo ""

  wait "$SERVER_PID"
else
  echo "An existing server is handling this viewer session."
fi
