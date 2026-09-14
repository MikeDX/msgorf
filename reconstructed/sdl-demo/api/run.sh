#!/usr/bin/env bash
# Start the score/replay API (SQLite) on 127.0.0.1:8091
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/uvicorn server:app --host 127.0.0.1 --port 8091
# Open http://127.0.0.1:8091/ for the game (serves ../web) + /api/
