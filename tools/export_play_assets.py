#!/usr/bin/env python3
"""Regenerate play/assets.json from MSGORPAT pattern sources + INDEX/ANIM-MAP."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISK = ROOT / "extracted/msgorf_floppy_files/MSGORPAT_Disk"
OUT = ROOT / "play" / "assets.json"


def main() -> None:
    index_text = "".join(chr(b) if 32 <= b < 127 else "\n" for b in (DISK / "INDEX").read_bytes())
    index = {m.group(2): m.group(3).strip() for m in re.finditer(r"(SC|NC)=\s*(\S+)\s*\(\s*([^)]*)\)", index_text)}
    am = "".join(chr(b) if 32 <= b < 127 else "\n" for b in (DISK / "ANIM-MAP").read_bytes())
    amap = {m.group(2): m.group(1) for m in re.finditer(r"(\S+)\s+(\S+)\s+AT!", am)}

    patterns: dict = {}
    for p in DISK.iterdir():
        if not p.is_file():
            continue
        if not (p.name.endswith("-P") or p.name in {"BANG", "NULPAT", "PLY-P", "GORF-P", "CLONE-P"}):
            continue
        text = "".join(chr(b) if 32 <= b < 127 else "\n" for b in p.read_bytes())
        for m in re.finditer(r"PATTERN\s+([A-Za-z0-9\-]+)([\s\S]*?)(?=PATTERN\s+|$)", text):
            name, body = m.group(1), m.group(2)
            rows = []
            for sm in re.finditer(r"~([^~^]*?)\^", body, re.S):
                digits = re.sub(r"[^0-3]", "", sm.group(1))
                if digits:
                    rows.append(digits)
            if not rows:
                for line in body.splitlines():
                    nums = re.findall(r"\b([0-3]{4})\b", line)
                    if len(nums) >= 2:
                        rows.append("".join(nums))
            if rows:
                w = max(len(r) for r in rows)
                patterns[name] = {"name": name, "w": w, "h": len(rows), "rows": [r.ljust(w, "0")[:w] for r in rows]}

    aliases = {
        "SPINV": "COMC5",
        "SMINE": "SMINE0",
        "BANGA": "FBEXP4",
        "BANGP": "FBEXP1",
        "CLONETBL": "CLN0",
        "P1UP": "INDICATING",
        "P2UP": "INDICATING",
        "LAZON": "LAZON",
    }
    roster = []
    for idx_name, desc in index.items():
        pat_name = amap.get(idx_name)
        resolved = aliases.get(pat_name, pat_name) if pat_name else None
        pix = patterns.get(resolved) if resolved else None
        roster.append(
            {
                "id": idx_name,
                "desc": desc,
                "anim_map": pat_name,
                "pattern": resolved if pix else None,
                "has_pixels": bool(pix),
                "w": pix["w"] if pix else None,
                "h": pix["h"] if pix else None,
            }
        )
    if "NULPAT" not in patterns:
        patterns["NULPAT"] = {"name": "NULPAT", "w": 1, "h": 1, "rows": ["0"]}

    OUT.write_text(
        json.dumps(
            {"index": index, "anim_map": amap, "patterns": patterns, "roster": roster},
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes), {len(patterns)} patterns, {len(roster)} roster")


if __name__ == "__main__":
    main()
