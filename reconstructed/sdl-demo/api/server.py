"""Ms. Gorf score + replay API (SQLite).

Validates each submission by re-simulating the replay with msgorf_verify
(headless game tick loop). Duplicate replays (same blob hash) return the
existing run id. Bad payloads are rejected with cheap checks before verify.
"""
from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
import sqlite3
import struct
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "msgorf.sqlite3"

# Hard limits — fail fast before spawning the verifier.
MAX_REPLAY_BYTES = 192 * 1024
MIN_REPLAY_BYTES = 32  # magic + minimal header
MAX_NAME_LEN = 24
MAX_SCORE = 5_000_000
MAX_TICKS = 60 * 60 * 30  # 30 minutes @ 60Hz
MIN_TICKS = 30  # ~0.5s — reject empty/trivial blobs
MAX_EVENTS = 20000

# Rate limits (per client IP)
RATE_POST_WINDOW_S = 60.0
RATE_POST_MAX = 4
RATE_HOUR_WINDOW_S = 3600.0
RATE_HOUR_MAX = 20
RATE_FAIL_WINDOW_S = 300.0
RATE_FAIL_MAX = 8  # bad verifies / junk → temporary cooldown

VERIFY_BIN = os.environ.get("MSGORF_VERIFY", "/usr/local/bin/msgorf_verify")
VERIFY_SCRIPT = os.environ.get("MSGORF_VERIFY_SCRIPT", "")
VERIFY_TIMEOUT_S = float(os.environ.get("MSGORF_VERIFY_TIMEOUT", "20"))
VERIFY_SLOTS = int(os.environ.get("MSGORF_VERIFY_SLOTS", "2"))

app = FastAPI(title="Ms. Gorf API", version="1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_rate_post: dict[str, list[float]] = {}
_rate_hour: dict[str, list[float]] = {}
_rate_fail: dict[str, list[float]] = {}
_verify_sem = threading.Semaphore(max(1, VERIFY_SLOTS))


def _db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
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
        for row in conn.execute(
            "SELECT id, replay FROM runs WHERE replay_hash IS NULL OR replay_hash = ''"
        ).fetchall():
            h = hashlib.sha256(row["replay"]).hexdigest()
            conn.execute("UPDATE runs SET replay_hash = ? WHERE id = ?", (h, row["id"]))
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
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created_at DESC)"
        )


@app.on_event("startup")
def startup() -> None:
    _init_db()


def _b64url_decode(s: str) -> bytes:
    if len(s) > MAX_REPLAY_BYTES * 2 + 64:
        raise HTTPException(413, "replay too large")
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
        return xff.split(",")[0].strip()[:64]
    if req.client:
        return req.client.host
    return "unknown"


def _prune(bucket: list[float], window: float, now: float) -> None:
    bucket[:] = [t for t in bucket if now - t < window]


def _hit(store: dict[str, list[float]], ip: str, window: float, limit: int) -> bool:
    """Return True if under limit (and record a hit)."""
    now = time.time()
    bucket = store.setdefault(ip, [])
    _prune(bucket, window, now)
    if len(bucket) >= limit:
        return False
    bucket.append(now)
    return True


def _fail_hit(ip: str) -> None:
    now = time.time()
    bucket = _rate_fail.setdefault(ip, [])
    _prune(bucket, RATE_FAIL_WINDOW_S, now)
    bucket.append(now)


def _fail_blocked(ip: str) -> bool:
    now = time.time()
    bucket = _rate_fail.setdefault(ip, [])
    _prune(bucket, RATE_FAIL_WINDOW_S, now)
    return len(bucket) >= RATE_FAIL_MAX


def _u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def _parse_replay_header(raw: bytes) -> dict[str, Any]:
    """Cheap structural checks before spawning the WASM verifier."""
    if len(raw) < MIN_REPLAY_BYTES or len(raw) > MAX_REPLAY_BYTES:
        raise HTTPException(400, "replay size out of range")
    if raw[:4] != b"MGR1":
        raise HTTPException(400, "not an Ms. Gorf replay")
    if len(raw) < 7:
        raise HTTPException(400, "truncated replay")
    ver = raw[4]
    if ver != 1:
        raise HTTPException(400, "unsupported replay version")
    bid_len = raw[6]
    if bid_len > 64:
        raise HTTPException(400, "bad build id")
    off = 7
    if off + bid_len + 16 > len(raw):
        raise HTTPException(400, "truncated replay header")
    build_id = raw[off : off + bid_len].decode("ascii", errors="replace")
    off += bid_len
    seed = _u32(raw, off)
    score = _u32(raw, off + 4)
    ticks = _u32(raw, off + 8)
    nevents = _u32(raw, off + 12)
    off += 16
    if score > MAX_SCORE:
        raise HTTPException(400, "score too high")
    if ticks < MIN_TICKS or ticks > MAX_TICKS:
        raise HTTPException(400, "tick count out of range")
    if nevents > MAX_EVENTS:
        raise HTTPException(400, "too many input events")
    # Each event is 4 (tick) + 14 (snap) = 18 bytes
    need = off + nevents * 18
    if need > len(raw):
        raise HTTPException(400, "truncated event stream")
    if need < len(raw) - 32:
        # Trailing junk is suspicious but allow a little padding
        raise HTTPException(400, "replay has trailing junk")
    return {
        "build_id": build_id,
        "seed": seed,
        "score": score,
        "ticks": ticks,
        "nevents": nevents,
    }


def _verify_cmd() -> list[str]:
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

    if not _verify_sem.acquire(blocking=False):
        raise HTTPException(503, "verifier busy — try again shortly")

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
        _verify_sem.release()
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
    score: int = Field(ge=0, le=MAX_SCORE)
    name: str = Field(default="", max_length=64)
    replay_b64: str = Field(min_length=8, max_length=MAX_REPLAY_BYTES * 2 + 8)
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
    if _fail_blocked(ip):
        raise HTTPException(429, "too many rejected submissions")
    if not _hit(_rate_post, ip, RATE_POST_WINDOW_S, RATE_POST_MAX):
        raise HTTPException(429, "slow down")
    if not _hit(_rate_hour, ip, RATE_HOUR_WINDOW_S, RATE_HOUR_MAX):
        raise HTTPException(429, "hourly limit reached")

    # Fast rejects before base64 decode of huge payloads
    if len(body.replay_b64) > MAX_REPLAY_BYTES * 2 + 8:
        _fail_hit(ip)
        raise HTTPException(413, "replay too large")

    try:
        raw = _b64url_decode(body.replay_b64)
        header = _parse_replay_header(raw)
        if body.score != int(header["score"]):
            raise HTTPException(400, "score does not match replay header")
        if body.ticks is not None and int(body.ticks) != int(header["ticks"]):
            raise HTTPException(400, "ticks do not match replay header")
    except HTTPException:
        _fail_hit(ip)
        raise

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

    try:
        verified = _verify_replay(raw)
    except HTTPException:
        _fail_hit(ip)
        raise

    if verified >= 0 and verified != int(body.score):
        _fail_hit(ip)
        raise HTTPException(
            400,
            f"score mismatch: client={body.score} verified={verified}",
        )
    score = verified if verified >= 0 else int(body.score)

    run_id = secrets.token_urlsafe(8)
    name = _clean_name(body.name)
    build_id = (body.build_id or header.get("build_id") or "dev")[:64]
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
                    header["seed"] if body.seed is None else body.seed,
                    score,
                    header["ticks"] if body.ticks is None else body.ticks,
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
    if not re.fullmatch(r"[\w\-]{6,32}", run_id or ""):
        raise HTTPException(404, "run not found")
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
def scores(
    limit: int = 20,
    build_id: str | None = None,
    period: str = "all",
) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 100))
    period = (period or "all").lower()
    now = time.time()
    since: float | None
    if period in ("day", "today", "d"):
        since = now - 86400.0
    elif period in ("week", "w"):
        since = now - 86400.0 * 7
    else:
        since = None

    clauses: list[str] = []
    args: list[Any] = []
    if build_id:
        clauses.append("build_id = ?")
        args.append(build_id[:64])
    if since is not None:
        clauses.append("created_at >= ?")
        args.append(since)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    args.append(limit)
    sql = f"""
        SELECT id, name, score, build_id, created_at
        FROM runs{where}
        ORDER BY score DESC, created_at ASC
        LIMIT ?
    """
    with _db() as conn:
        rows = conn.execute(sql, tuple(args)).fetchall()
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
