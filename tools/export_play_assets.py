#!/usr/bin/env python3
"""Regenerate play/assets.json from MSGORPAT pattern sources + INDEX/ANIM-MAP.

Adds per-pattern palette bytes (from PATTERN headers) and animation frame lists
grouped from the same source files (CLONE, KAMI, SMINE, BANG explosions).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISK = ROOT / "extracted" / "msgorf_floppy_files" / "MSGORPAT_Disk"
OUT = ROOT / "play" / "assets.json"

# Frame sequences from disk pattern files (names as PATTERN … on disk)
ANIMATIONS = {
    "CLONETBL": ["CLN0", "CLN32", "CLN64"],
    "SPINV": ["COMC5", "COMC5A", "COMC5B", "COMC6"],
    "SMINE": ["SMINE0", "SMINE1"],
    # FBEXP1–4 are packed QUADPAT strips (poor 2D preview); 5–6 are full frames
    "BANGA": ["FBEXP5", "FBEXP6"],
    "BANGP": ["FBEXP5", "FBEXP6"],
}


# Shared 2bpp display palette (lab hypothesis from reading the art + prototype photos).
# Digit 0..3 → black, yellow, blue, red. PATTERN header HEX bytes are still stored
# as palette_bytes for RE, but are *not* treated as unique per-sprite RGB.
FIXED_PALETTE_RGB = [
    [0, 0, 0],  # 0 black
    [240, 200, 32],  # 1 yellow
    [48, 96, 220],  # 2 blue
    [220, 40, 48],  # 3 red
]


def parse_file_patterns(text: str) -> dict:
    out: dict = {}
    for m in re.finditer(
        r"(?:PATTERN|DATA)\s+([A-Za-z0-9\-]+)([\s\S]*?)(?=(?:PATTERN|DATA)\s+|$)",
        text,
    ):
        name, body = m.group(1), m.group(2)
        rows: list[str] = []
        for sm in re.finditer(r"~([^~^]*?)\^", body, re.S):
            digits = re.sub(r"[^0-3]", "", sm.group(1))
            if digits:
                rows.append(digits)
        if not rows:
            for line in body.splitlines():
                nums = re.findall(r"\b([0-3]{4})\b", line)
                if len(nums) >= 2:
                    rows.append("".join(nums))
        if not rows:
            continue
        w = max(len(r) for r in rows)
        rows = [r.ljust(w, "0")[:w] for r in rows]
        # Palette: HEX aa B, bb B, cc B, after header
        pal = [0x10, 0x20, 0x30]
        pm = re.search(
            r"HEX\s+([0-9A-Fa-f]+)\s+B,\s*([0-9A-Fa-f]+)\s+B,\s*([0-9A-Fa-f]+)\s+B,",
            body,
        )
        if pm:
            pal = [int(pm.group(i), 16) for i in (1, 2, 3)]
        out[name] = {
            "name": name,
            "w": w,
            "h": len(rows),
            "rows": rows,
            "palette_bytes": pal,
            "palette_rgb": [list(c) for c in FIXED_PALETTE_RGB],
        }
    return out


def main() -> None:
    index_text = "".join(
        chr(b) if 32 <= b < 127 else "\n" for b in (DISK / "INDEX").read_bytes()
    )
    index = {
        m.group(2): m.group(3).strip()
        for m in re.finditer(r"(SC|NC)=\s*(\S+)\s*\(\s*([^)]*)\)", index_text)
    }
    am = "".join(
        chr(b) if 32 <= b < 127 else "\n" for b in (DISK / "ANIM-MAP").read_bytes()
    )
    amap = {m.group(2): m.group(1) for m in re.finditer(r"(\S+)\s+(\S+)\s+AT!", am)}

    patterns: dict = {}
    for p in DISK.iterdir():
        if not p.is_file():
            continue
        if not (
            p.name.endswith("-P")
            or p.name in {"BANG", "NULPAT", "PLY-P", "GORF-P", "CLONE-P", "PLUP"}
        ):
            continue
        text = "".join(chr(b) if 32 <= b < 127 else "\n" for b in p.read_bytes())
        patterns.update(parse_file_patterns(text))

    if "NULPAT" not in patterns:
        patterns["NULPAT"] = {
            "name": "NULPAT",
            "w": 1,
            "h": 1,
            "rows": ["0"],
            "palette_bytes": [0x10, 0x20, 0x30],
            "palette_rgb": [list(c) for c in FIXED_PALETTE_RGB],
        }

    aliases = {
        "SPINV": "COMC5",
        "SMINE": "SMINE0",
        "BANGA": "FBEXP5",
        "BANGP": "FBEXP5",
        "CLONETBL": "CLN0",
        "P1UP": "P1UP",
        "P2UP": "P2UP",
        "LAZON": "LAZON",
    }

    # Only keep animation frames that exist
    animations = {
        k: [f for f in frames if f in patterns]
        for k, frames in ANIMATIONS.items()
        if any(f in patterns for f in frames)
    }

    roster = []
    for idx_name, desc in index.items():
        pat_name = amap.get(idx_name)
        resolved = aliases.get(pat_name, pat_name) if pat_name else None
        pix = patterns.get(resolved) if resolved else None
        frames = animations.get(pat_name or "", [])
        if not frames and resolved:
            frames = [resolved]
        # P1/P2 UP flash per INDEX comment
        if idx_name in ("P1Ui", "P2Ui") and resolved:
            frames = [resolved, "NULPAT"]
        roster.append(
            {
                "id": idx_name,
                "desc": desc,
                "anim_map": pat_name,
                "pattern": resolved if pix else None,
                "frames": frames,
                "has_pixels": bool(pix),
                "w": pix["w"] if pix else None,
                "h": pix["h"] if pix else None,
            }
        )

    assets = {
        "index": index,
        "anim_map": amap,
        "patterns": patterns,
        "animations": animations,
        "roster": roster,
        "palette_note": (
            "Shared 2bpp palette hypothesis: 0=black 1=yellow 2=blue 3=red "
            "(same for all patterns). Header HEX color bytes kept as palette_bytes "
            "for RE only — not used as per-sprite RGB."
        ),
        "palette_rgb": FIXED_PALETTE_RGB,
    }
    OUT.write_text(json.dumps(assets, indent=2) + "\n")
    js = ROOT / "play" / "assets.js"
    js.write_text(
        "/* auto-generated by export_play_assets.py — do not edit */\n"
        "window.MSGORF_ASSETS = "
        + json.dumps(assets, separators=(",", ":"))
        + ";\n"
    )
    print(
        f"wrote {OUT} ({OUT.stat().st_size} bytes) + {js.name}, "
        f"{len(patterns)} patterns, {len(animations)} anims, {len(roster)} roster"
    )


if __name__ == "__main__":
    main()
