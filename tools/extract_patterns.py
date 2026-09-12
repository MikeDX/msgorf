#!/usr/bin/env python3
"""Decode ASCII hex-digit pattern art (0-3) from MSGORF corrected image / screens."""
from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUT = ROOT / "extracted" / "patterns"
PALETTE = {
    0: (0, 0, 0),
    1: (40, 90, 220),
    2: (230, 50, 40),
    3: (245, 245, 245),
}


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int]], scale: int = 4) -> None:
    w, h = width * scale, height * scale
    rows = []
    for y in range(h):
        row = [0]  # filter none
        src_y = y // scale
        for x in range(w):
            r, g, b = pixels[src_y * width + (x // scale)]
            row.extend((r, g, b))
        rows.append(bytes(row))
    raw = b"".join(rows)
    compressed = zlib.compress(raw, 9)
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    path.write_bytes(png)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data = (WORK / "MSGORF.img.corrected").read_bytes()
    text = "".join(chr(b) if 32 <= b < 127 else "\n" for b in data)
    seqs = re.findall(r"~([^~^]*?)\^", text, re.S)
    rows = [re.sub(r"[^0-3]", "", s) for s in seqs]
    rows = [r for r in rows if r]
    meta = {
        "sequences": len(rows),
        "row_lengths": sorted({len(r) for r in rows}),
        "header_hint": "PATTERN GORF4A 3 B, 3 B, 64 B, 26 B, ... QUADPAT",
    }
    (OUT / "gorf4a_meta.json").write_text(__import__("json").dumps(meta, indent=2) + "\n")
    if not rows:
        print("No pattern rows found")
        return
    # Each ~^ with 256 digits = 4 scanlines of 64 pixels
    scan = []
    for r in rows:
        if len(r) >= 256:
            for i in range(0, 256, 64):
                scan.append(r[i : i + 64])
        elif len(r) == 64:
            scan.append(r)
    pixels = []
    for row in scan:
        for ch in row:
            pixels.append(PALETTE[int(ch)])
    h, w = len(scan), 64
    write_png(OUT / "gorf4a_strip.png", w, h, pixels, scale=6)
    # Split into 4 QUADPAT frames if divisible
    if h % 4 == 0:
        fh = h // 4
        for fi in range(4):
            chunk_pix = pixels[fi * fh * w : (fi + 1) * fh * w]
            write_png(OUT / f"gorf4a_frame{fi}.png", w, fh, chunk_pix, scale=8)
    print(f"Wrote strip {w}x{h}, sequences={len(rows)}")
    # Move/copy prior preview if present
    old = ROOT / "gorf4a_pattern_preview.png"
    if old.exists():
        (OUT / "gorf4a_pattern_preview_legacy.png").write_bytes(old.read_bytes())


if __name__ == "__main__":
    main()
