#!/usr/bin/env python3
"""Decode simple pattern records from XC.PATTERNS @ ROMSTART.

Working format (simple non-animation patterns):
  ATBL[i] -> pointer P
  bytes at P:
    [0] [1]  unknown (often similar magnitude)
    [2]      bytes_per_row  (2bpp => width = bytes_per_row * 4)
    [3]      height
    [4..6]   palette-ish bytes for colors 1..3
    [7..]    packed pixels, MSB-first 2bpp, bytes_per_row * height

Animation slots (BANGA, BANGP, CLONETBL, SPINV, SMINE, …) point into
0x4200-range tables of frame pointers — not decoded here yet.

Provenance: pixel blobs match play/assets.json rows packed the same way
(flat MSB 2bpp), verified for GORF-PAT, PLY1-P, LAZON, etc.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROMSTART = 0x4000
DEFAULT_ROM = ROOT / "out" / "msgorf_patterns_at_4000.bin"

# ANIM-MAP order (INDEX SC=/NC= slots)
ATBL_NAMES = [
    "NULPAT",
    "PLY1-P",
    "PLY2-P",
    "SBASE",
    "P1UP",
    "P2UP",
    "BANGA",
    "BANGP",
    "CLONETBL",
    "GORF-PAT",
    "LAZON",
    "SPINV",
    "SMINE",
    "SHLD-P",
    "MITE-P",
    "TRION-P",
    "DEB-P",
    "HK-P",
    "GB-P",
    "GRD-P",
]


@dataclass
class XcPattern:
    name: str
    index: int
    ptr: int
    w: int
    h: int
    bytes_per_row: int
    pix: list[int]  # 0..3 flat
    header: bytes


def unpack_2bpp_msb(data: bytes, w: int, h: int, bpr: int) -> list[int]:
    pix: list[int] = []
    for row in range(h):
        base = row * bpr
        row_pix: list[int] = []
        for b in data[base : base + bpr]:
            for shift in (6, 4, 2, 0):
                row_pix.append((b >> shift) & 3)
        pix.extend(row_pix[:w])
    return pix


def read_atbl(mem: bytes, base: int = ROMSTART, count: int = 20) -> list[int]:
    return [struct.unpack_from("<H", mem, base + i * 2)[0] for i in range(count)]


def decode_simple(mem: bytes, index: int, name: str | None = None) -> XcPattern | None:
    """Decode one ATBL slot if it looks like a simple pattern record."""
    if name is None:
        name = ATBL_NAMES[index] if index < len(ATBL_NAMES) else f"slot{index}"
    ptr = read_atbl(mem)[index]
    if ptr < ROMSTART or ptr >= 0x10000 - 8:
        return None
    # Animation tables live near PT-HERE
    if 0x4200 <= ptr < 0x4300:
        return None
    hdr = mem[ptr : ptr + 7]
    bpr = hdr[2]
    h = hdr[3]
    if bpr == 0 or h == 0 or bpr > 64 or h > 64:
        return None
    w = bpr * 4
    nbytes = bpr * h
    data = mem[ptr + 7 : ptr + 7 + nbytes]
    if len(data) != nbytes:
        return None
    pix = unpack_2bpp_msb(data, w, h, bpr)
    return XcPattern(name, index, ptr, w, h, bpr, pix, bytes(hdr))


def decode_all_simple(mem: bytes) -> list[XcPattern]:
    out: list[XcPattern] = []
    for i, name in enumerate(ATBL_NAMES):
        p = decode_simple(mem, i, name)
        if p:
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    ap.add_argument("-o", type=Path, default=ROOT / "out" / "xc_decode_report.json")
    args = ap.parse_args()
    mem = args.rom.read_bytes()
    if len(mem) != 0x10000:
        raise SystemExit(f"expected 64K image, got {len(mem)}")
    patterns = decode_all_simple(mem)
    report = {
        "rom": str(args.rom.relative_to(ROOT)),
        "rom_sha256": hashlib.sha256(mem).hexdigest(),
        "format_note": "7-byte header + MSB 2bpp; width=bpr*4; height=hdr[3]",
        "decoded": [
            {
                "name": p.name,
                "index": p.index,
                "ptr": hex(p.ptr),
                "w": p.w,
                "h": p.h,
                "header_hex": p.header.hex(),
                "pix_sha256": hashlib.sha256(bytes(p.pix)).hexdigest(),
            }
            for p in patterns
        ],
        "skipped_animation_or_complex": [
            n
            for i, n in enumerate(ATBL_NAMES)
            if decode_simple(mem, i, n) is None
        ],
    }
    args.o.parent.mkdir(parents=True, exist_ok=True)
    args.o.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
