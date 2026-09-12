#!/usr/bin/env python3
"""Normalize Ms. Gorf disk images to correct bit polarity.

Decoded .img files in this archive are bit-inverted. This tool writes
work/<name>.img.corrected = XOR 0xFF of each byte (same content as .inv
trimmed to .img length) and prints SHA256 for originals and outputs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

SOURCES = [
    {
        "id": "MSGORF",
        "img": ROOT / "MSGORF" / "msgorf_scp.img",
        "inv": ROOT / "MSGORF" / "msgorf.inv",
    },
    {
        "id": "MSGORPAT",
        "img": ROOT / "MSGORPAT" / "MSGORPAT_IMD.img",
        "inv": ROOT / "MSGORPAT" / "MSGORPAT_IMD.img.inv",
    },
    {
        "id": "MSGPATLD",
        "img": ROOT / "MSGPATLD" / "MSGPATLD_IMD.img",
        "inv": ROOT / "MSGPATLD" / "MSGPATLD_IMD.img.inv",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    report = []
    for src in SOURCES:
        img = src["img"].read_bytes()
        inv = src["inv"].read_bytes()
        corrected = bytes(b ^ 0xFF for b in img)
        inv_trim = inv[: len(img)]
        match_inv = corrected == inv_trim
        out = WORK / f"{src['id']}.img.corrected"
        out.write_bytes(corrected)
        entry = {
            "id": src["id"],
            "img_path": str(src["img"].relative_to(ROOT)),
            "img_size": len(img),
            "img_sha256": sha256(img),
            "inv_path": str(src["inv"].relative_to(ROOT)),
            "inv_size": len(inv),
            "inv_sha256": sha256(inv),
            "corrected_path": str(out.relative_to(ROOT)),
            "corrected_sha256": sha256(corrected),
            "corrected_matches_inv_trimmed": match_inv,
            "blocks_1024": len(img) // 1024,
            "remainder": len(img) % 1024,
        }
        report.append(entry)
        print(
            f"{src['id']}: {len(img)} bytes, "
            f"matches .inv={match_inv}, "
            f"-> {out.name} sha256={entry['corrected_sha256'][:16]}..."
        )

    (WORK / "normalize_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {WORK / 'normalize_report.json'}")


if __name__ == "__main__":
    main()
