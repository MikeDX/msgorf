"""Ms. Gorf score + replay API (SQLite).

Validates each submission by re-simulating the replay with msgorf_verify
(headless game tick loop). Duplicate replays (same blob hash) are rejected
as new rows and return the existing run id.
"""
from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "msgorf.sqlite3"
MAX_REPLAY_BYTES = 512 * 1024
MAX_NAME_LEN = 24
RATE_WINDOW_S = 60.0
RATE_MAX_POSTS = 20
VERIFY_BIN = os.environ.get("MSGORF_VERIFY", "/usr/local/bin/msgorf_verify")
VERIFY_SCRIPT = os.environ.get("MSGORF_VERIFY_SCRIPT", "")
VERIFY_TIMEOUT_S = float(os.environ.get("MSGORF_VERIFY_TIMEOUT", "120"))

app = FastAPI(title="Ms. Gorf API", version="1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_rate: dict[str, list[float]] = {}


def _db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
              id TEXT PRIMARY KEY,
              created_at REAL NOT NULL,
              build_id TEXT NOT NULL,
              seed INTEGER,
              score INTEGER NOT NULL,
              ticks INTEGER,
              name TEXT,
              replay BLOB NOT NULL,
              replay_hash TEXT
            )
            """
        )
        cols = {r[1] for r in conn.execute("PRAGMA table_info(runs)").fetchall()}
        if "replay_hash" not in cols:
            conn.execute("ALTER TABLE runs ADD COLUMN replay_hash TEXT")
        # Backfill hashes for older rows
        for row in conn.execute(
            "SELECT id, replay FROM runs WHERE replay_hash IS NULL OR replay_hash = ''"
        ).fetchall():
            h = hashlib.sha256(row["replay"]).hexdigest()
            conn.execute("UPDATE runs SET replay_hash = ? WHERE id = ?", (h, row["id"]))
        # Drop duplicate replays (keep earliest) before unique index
        dupes = conn.execute(
            """
            SELECT replay_hash FROM runs
            WHERE replay_hash IS NOT NULL AND replay_hash != ''
            GROUP BY replay_hash HAVING COUNT(*) > 1
            """
        ).fetchall()
        for d in dupes:
            rows = conn.execute(
                """
                SELECT id FROM runs WHERE replay_hash = ?
                ORDER BY created_at ASC, id ASC
                """,
                (d["replay_hash"],),
            ).fetchall()
            for extra in rows[1:]:
                conn.execute("DELETE FROM runs WHERE id = ?", (extra["id"],))
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_runs_hash ON runs(replay_hash)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_runs_score ON runs(score DESC, created_at DESC)"
        )


@app.on_event("startup")
def startup() -> None:
    _init_db()


def _b64url_decode(s: str) -> bytes:
    s = s.replace("-", "+").replace("_", "/")
    pad = (-len(s)) % 4
    if pad:
        s += "=" * pad
    try:
        return base64.b64decode(s, validate=False)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, "invalid replay_b64") from exc


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _clean_name(name: str | None) -> str:
    if not name:
        return ""
    name = re.sub(r"[^\w \-.'!]", "", name, flags=re.UNICODE).strip()
    return name[:MAX_NAME_LEN]


def _client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if req.client:
        return req.client.host
    return "unknown"


def _rate_ok(ip: str) -> bool:
    now = time.time()
    bucket = _rate.setdefault(ip, [])
    bucket[:] = [t for t in bucket if now - t < RATE_WINDOW_S]
    if len(bucket) >= RATE_MAX_POSTS:
        return False
    bucket.append(now)
    return True


def _verify_cmd() -> list[str]:
    """Return argv prefix for the headless verifier."""
    if VERIFY_BIN == "node" or VERIFY_BIN.endswith("node"):
        script = VERIFY_SCRIPT or str(Path(__file__).resolve().parent / "msgorf_verify.js")
        return ["node", script]
    return [VERIFY_BIN]


def _verify_available() -> bool:
    if VERIFY_BIN == "node" or VERIFY_BIN.endswith("node"):
        script = VERIFY_SCRIPT or str(Path(__file__).resolve().parent / "msgorf_verify.js")
        return Path(script).is_file()
    return Path(VERIFY_BIN).is_file()


def _verify_replay(raw: bytes) -> int:
    """Re-simulate the replay at full speed; return verified score."""
    if not _verify_available():
        if os.environ.get("MSGORF_ALLOW_UNVERIFIED") == "1":
            return -1
        raise HTTPException(503, "score verifier unavailable")

    fd, path = tempfile.mkstemp(prefix="msgorf_", suffix=".mgr1")
    os.close(fd)
    try:
        Path(path).write_bytes(raw)
        proc = subprocess.run(
            [*_verify_cmd(), path],
            capture_output=True,
            text=True,
            timeout=VERIFY_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(400, "replay verification timed out") from exc
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "verify failed").strip()
        raise HTTPException(400, f"invalid replay: {err[:240]}")
    try:
        return int((proc.stdout or "").strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise HTTPException(400, "verifier returned no score") from exc


class RunIn(BaseModel):
    build_id: str = Field(default="dev", max_length=64)
    score: int = Field(ge=0, le=99_999_999)
    name: str = Field(default="", max_length=64)
    replay_b64: str = Field(min_length=8, max_length=MAX_REPLAY_BYTES * 2)
    seed: int | None = None
    ticks: int | None = None


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "verify": _verify_available(),
    }


@app.post("/api/runs")
def create_run(body: RunIn, request: Request) -> dict[str, Any]:
    ip = _client_ip(request)
    if not _rate_ok(ip):
        raise HTTPException(429, "slow down")
    raw = _b64url_decode(body.replay_b64)
    if len(raw) > MAX_REPLAY_BYTES:
        raise HTTPException(413, "replay too large")
    if len(raw) < 8 or raw[:4] != b"MGR1":
        raise HTTPException(400, "not an Ms. Gorf replay")

    replay_hash = hashlib.sha256(raw).hexdigest()
    with _db() as conn:
        existing = conn.execute(
            "SELECT id, score, name FROM runs WHERE replay_hash = ?",
            (replay_hash,),
        ).fetchone()
    if existing:
        return {
            "id": existing["id"],
            "score": int(existing["score"]),
            "name": existing["name"] or "",
            "duplicate": True,
            "verified": True,
        }

    verified = _verify_replay(raw)
    if verified >= 0 and verified != int(body.score):
        raise HTTPException(
            400,
            f"score mismatch: client={body.score} verified={verified}",
        )
    score = verified if verified >= 0 else int(body.score)

    run_id = secrets.token_urlsafe(8)
    name = _clean_name(body.name)
    build_id = (body.build_id or "dev")[:64]
    with _db() as conn:
        try:
            conn.execute(
                """
                INSERT INTO runs
                  (id, created_at, build_id, seed, score, ticks, name, replay, replay_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    time.time(),
                    build_id,
                    body.seed,
                    score,
                    body.ticks,
                    name,
                    raw,
                    replay_hash,
                ),
            )
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT id, score, name FROM runs WHERE replay_hash = ?",
                (replay_hash,),
            ).fetchone()
            if row:
                return {
                    "id": row["id"],
                    "score": int(row["score"]),
                    "name": row["name"] or "",
                    "duplicate": True,
                    "verified": True,
                }
            raise HTTPException(409, "duplicate replay") from None

    return {
        "id": run_id,
        "score": score,
        "name": name,
        "duplicate": False,
        "verified": verified >= 0,
    }


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    with _db() as conn:
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if not row:
        raise HTTPException(404, "run not found")
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "build_id": row["build_id"],
        "seed": row["seed"],
        "score": row["score"],
        "ticks": row["ticks"],
        "name": row["name"] or "",
        "replay_b64": _b64url_encode(row["replay"]),
    }


@app.get("/api/scores")
def scores(limit: int = 20, build_id: str | None = None) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 50))
    with _db() as conn:
        if build_id:
            rows = conn.execute(
                """
                SELECT id, name, score, build_id, created_at
                FROM runs WHERE build_id = ?
                ORDER BY score DESC, created_at ASC
                LIMIT ?
                """,
                (build_id[:64], limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, name, score, build_id, created_at
                FROM runs
                ORDER BY score DESC, created_at ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [
        {
            "id": r["id"],
            "name": r["name"] or "",
            "score": r["score"],
            "build_id": r["build_id"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


# Local all-in-one only (not used in the Traefik/docker API image).
_WEB = Path(__file__).resolve().parent.parent / "web"
if os.environ.get("MSGORF_SERVE_WEB", "1") != "0" and _WEB.is_dir():
    app.mount("/", StaticFiles(directory=str(_WEB), html=True), name="web")
