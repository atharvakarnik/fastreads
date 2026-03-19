#!/bin/bash
set -e

cd "$(dirname "$0")"

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"

URL="http://127.0.0.1:8000/viewer.html"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python 3.10+ is required but no Python interpreter was found."
  exit 1
fi

if ! "$PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "Python 3.10+ is required."
  "$PY" --version 2>/dev/null || true
  exit 1
fi

echo "Starting PET Viewer server..."
$PY server.py &
SERVER_PID=$!

cleanup() {
  echo ""
  echo "Stopping PET Viewer server..."
  kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Waiting for server..."
if ! "$PY" - <<'PY'
import sys
import time
import urllib.request

url = "http://127.0.0.1:8000/viewer.html"
deadline = time.time() + 15

while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            if response.status == 200:
                raise SystemExit(0)
    except Exception:
        time.sleep(0.25)

raise SystemExit(1)
PY
then
  echo "Server did not become ready at $URL"
  exit 1
fi

open_viewer() {
  if [ "${NO_BROWSER:-0}" = "1" ]; then
    echo "NO_BROWSER=1 set; not opening a browser automatically."
    return 0
  fi

  case "$(uname -s)" in
    Darwin)
      open "$URL"
      return 0
      ;;
    Linux)
      if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
        if command -v xdg-open >/dev/null 2>&1; then
          xdg-open "$URL" >/dev/null 2>&1 &
          return 0
        fi
        if command -v gio >/dev/null 2>&1; then
          gio open "$URL" >/dev/null 2>&1 &
          return 0
        fi
        if command -v firefox >/dev/null 2>&1; then
          firefox "$URL" >/dev/null 2>&1 &
          return 0
        fi
      fi
      ;;
  esac

  echo "Open this URL in a browser:"
  echo "  $URL"
  return 0
}

echo "Opening viewer..."
open_viewer

echo ""
echo "PET Viewer started at:"
echo "  $URL"
echo ""
echo "Keep this Terminal window open while using the viewer."
echo "Press Ctrl+C here when done."
echo ""

wait "$SERVER_PID"
