#!/usr/bin/env bash
# Start the score/replay API (SQLite) on 127.0.0.1:8091
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
export MSGORF_SERVE_WEB="${MSGORF_SERVE_WEB:-1}"
if [[ -f msgorf_verify.js ]]; then
  export MSGORF_VERIFY=node
  export MSGORF_VERIFY_SCRIPT="$PWD/msgorf_verify.js"
else
  export MSGORF_ALLOW_UNVERIFIED=1
  echo "warning: msgorf_verify.js missing — run 'make prepare-verify' (unverified mode)" >&2
fi
exec .venv/bin/uvicorn server:app --host 127.0.0.1 --port 8091
# Open http://127.0.0.1:8091/ for the game (serves ../web) + /api/
