"""Ms. Gorf score + replay API (SQLite).

Local:
  pip install -r requirements.txt
  uvicorn server:app --host 127.0.0.1 --port 8091

Live: Docker service msgorf-api behind Traefik at
  https://msgorf.mikedx.co.uk/api/...
"""
from __future__ import annotations

import base64
import os
import re
import secrets
import sqlite3
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
              replay BLOB NOT NULL
            )
            """
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


class RunIn(BaseModel):
    build_id: str = Field(default="dev", max_length=64)
    score: int = Field(ge=0, le=99_999_999)
    name: str = Field(default="", max_length=64)
    replay_b64: str = Field(min_length=8, max_length=MAX_REPLAY_BYTES * 2)
    seed: int | None = None
    ticks: int | None = None


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
    run_id = secrets.token_urlsafe(8)
    name = _clean_name(body.name)
    build_id = (body.build_id or "dev")[:64]
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO runs (id, created_at, build_id, seed, score, ticks, name, replay)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                time.time(),
                build_id,
                body.seed,
                int(body.score),
                body.ticks,
                name,
                raw,
            ),
        )
    return {"id": run_id, "score": int(body.score), "name": name}


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
