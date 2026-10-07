#!/bin/bash
# ============================================================================
#  Matching-Singer-song — one-click launcher for macOS
#
#  Double-click this file to:
#    1. start the game server (if it isn't already running)
#    2. open the matching game in your default browser
#
#  No need to type a URL ever again. Close the Terminal window after the
#  browser opens and the game keeps running in the background.
#
#  Stop the game later with:  pkill -f uvicorn
# ============================================================================

cd "$(dirname "$0")" || exit 1

# 1. Make sure the server is running.
if curl -s -m 2 http://127.0.0.1:8000/health > /dev/null 2>&1; then
  echo "✓ Game server already running."
else
  echo "Starting the game server…"
  nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 >> /tmp/mss.log 2>&1 &
  sleep 2
  if curl -s -m 2 http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✓ Game server started."
  else
    echo "⚠ Server failed to start — check /tmp/mss.log"
    read -n 1 -s -r -p "Press any key to close…"
    exit 1
  fi
fi

# 2. Open the game.
open "http://127.0.0.1:8000/game"
echo "✓ Game opened in your browser. You can close this window."
echo

# Keep the window open a moment so the user can read the output.
sleep 2