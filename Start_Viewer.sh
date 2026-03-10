#!/bin/bash
set -e

cd "$(dirname "$0")"

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"

URL="http://127.0.0.1:8000/viewer.html"

echo "Starting PET Viewer server..."
$PY server.py &
SERVER_PID=$!

cleanup() {
  echo ""
  echo "Stopping PET Viewer server..."
  kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

sleep 1

echo "Opening viewer..."
open "$URL"

echo ""
echo "PET Viewer started at:"
echo "  $URL"
echo ""
echo "Keep this Terminal window open while using the viewer."
echo "Press Ctrl+C here when done."
echo ""

wait "$SERVER_PID"